"""
Generar el pipeline de preprocesamiento de imágenes con optimización de hiperparámetros asistida por LLM.
"""

import cv2
import numpy as np
import pytesseract
from eth_hash.auto import keccak

# --- Funciones base con metadatos de parámetros ---

def is_blurry(image, threshold=100):
    """
    Check if the image is blurry using the Laplacian variance method.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold


def correct_image_rotation(image, **params):
    """
    Detect and correct rotation.
    Params en metadata: {}
    """.format(params)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh>0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45: angle = -(90+angle)
    else: angle = -angle
    h,w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w//2,h//2), angle,1.0)
    out = cv2.warpAffine(image,M,(w,h),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    out.__metadata__ = {'angle': angle}
    return out


def make_denoise(h=10, template_window=7):
    """Factory de denoise con parámetros ajustables en metadata."""
    def _denoise(image):
        out = cv2.fastNlMeansDenoisingColored(image,None,h,h,template_window,21)
        out.__metadata__ = {'h':h,'template_window':template_window}
        return out
    _denoise.__name__ = f"denoise(h={h},tw={template_window})"
    return _denoise


def adjust_brightness_contrast(image, alpha=1.5, beta=0):
    """
    Ajusta brillo y contraste de la imagen.
    alpha: factor de contraste (1.0-3.0)
    beta: factor de brillo (0-100)
    """
    out = cv2.convertScaleAbs(image,alpha=alpha,beta=beta)
    out.__metadata__ = {'alpha':alpha,'beta':beta}
    return out


def resize_image(image, width=1024):
    """
    Redimensiona la imagen manteniendo la relación de aspecto.
    width: nuevo ancho deseado
    height: nuevo alto calculado
    
    retorna imagen redimensionada y metadatos
    """
    height = int(image.shape[0]*(width/image.shape[1]))
    out = cv2.resize(image,(width,height),interpolation=cv2.INTER_AREA)
    out.__metadata__ = {'width':width,'height':height}
    return out


def normalize_image(image, clipLimit=2.0, tileGrid=(8,8)):
    """
    Normaliza la imagen usando CLAHE (Contrast Limited Adaptive Histogram Equalization).
    clipLimit: límite de contraste
    tileGrid: tamaño de la cuadrícula para CLAHE
    
    retorna imagen normalizada y metadatos
    """
    lab = cv2.cvtColor(image,cv2.COLOR_BGR2LAB)
    l,a,b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clipLimit,tileGridSize=tileGrid)
    cl = clahe.apply(l)
    merged = cv2.merge((cl,a,b))
    out = cv2.cvtColor(merged,cv2.COLOR_LAB2BGR)
    out.__metadata__ = {'clipLimit':clipLimit,'tileGrid':tileGrid}
    return out


def auto_crop(image, margin=0):
    """
    Recorta la imagen automáticamente eliminando bordes vacíos.
    margin: margen a aplicar al recorte (en píxeles)
    
    retorna imagen recortada y metadatos
    """
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    _,th = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(th>0))
    x,y,w,h = cv2.boundingRect(coords)
    # aplicar margin
    x0,y0 = max(0,x-margin),max(0,y-margin)
    x1,y1 = min(image.shape[1],x+w+margin),min(image.shape[0],y+h+margin)
    out = image[y0:y1,x0:x1]
    out.__metadata__ = {'crop_box':(x0,y0,x1,y1)}
    return out

# Hash y metadata

def keccak_image_hash(image, fmt='.png'):
    """
    Genera un hash Keccak de la imagen.
    image: imagen a hashear
    fmt: formato de imagen ('.png', '.jpg', etc.)
    
    retorna el hash en formato hexadecimal Bytes32 (Solidity)
    """
    _,buf = cv2.imencode(fmt,image)
    data = buf.tobytes()
    return keccak(data).hex()

# --- Construcción de pipeline dinámico ---

def build_pipeline(param_config):
    """
    Recibe un diccionario con valores de hiperparámetros y devuelve lista de pasos.
    Ejemplo param_config:
      {
        'denoise': {'h':5,'template_window':3},
        'contrast': {'alpha':1.2,'beta':15},
        'resize': {'width': 800},
        'clahe': {'clipLimit':1.5,'tileGrid':(8,8)},
        'crop': {'margin':5}
      }
    """
    return [
        correct_image_rotation,
        make_denoise(**param_config.get('denoise',{})),
        lambda img: adjust_brightness_contrast(img, **param_config.get('contrast',{})),
        lambda img: resize_image(img, **param_config.get('resize',{})),
        lambda img: normalize_image(img, **param_config.get('clahe',{})),
        lambda img: auto_crop(img, **param_config.get('crop',{})),
    ]

# --- Evaluación de calidad ---

def evaluate_image_quality(orig, proc):
    """
    Retorna un diccionario con métricas: reducción de blur y ganancia en OCR.
    """
    b_orig = cv2.Laplacian(cv2.cvtColor(orig,cv2.COLOR_BGR2GRAY),cv2.CV_64F).var()
    b_proc = cv2.Laplacian(cv2.cvtColor(proc,cv2.COLOR_BGR2GRAY),cv2.CV_64F).var()
    text_orig = len(pytesseract.image_to_string(orig))
    text_proc = len(pytesseract.image_to_string(proc))
    return {
        'blur_reduction': b_proc - b_orig,
        'ocr_gain': text_proc - text_orig,
        'score': (b_proc - b_orig) + (text_proc - text_orig)
    }

# --- Optimización asistida ---

def optimize_pipeline(orig_image, param_space, llm_call, max_iter=5):
    """
    param_space: diccionario con listas de valores a muestrear.
    llm_call: función que recibe {orig, proc, metrics, params} y devuelve nuevo param_config.
    Devuelve mejor resultado.
    """
    best = {'score':-np.inf}
    for i in range(max_iter):
        # muestreo (aleatorio simple)
        params = {k: {sk: np.random.choice(v) for sk,v in sp.items()} for k,sp in param_space.items()}
        pipeline = build_pipeline(params)
        steps = pipeline
        img = orig_image.copy()
        for step in steps:
            img = step(img)
        metrics = evaluate_image_quality(orig_image, img)
        # pedir ajuste al LLM
        params = llm_call({
            'orig': orig_image,
            'proc': img,
            'metrics': metrics,
            'params': params
        })
        # re-evaluar con params sugeridos
        pipeline = build_pipeline(params)
        img2 = orig_image.copy()
        for step in pipeline:
            img2 = step(img2)
        metrics2 = evaluate_image_quality(orig_image, img2)
        if metrics2['score']>best['score']:
            best = {'score':metrics2['score'],'image':img2,'params':params,'metrics':metrics2}
    return best

# --- Ejemplo de llamada a LLM ---

def llm_adjust_callback(data):
    """
    data contiene orig, proc, metrics, params. Devuelve nuevo params.
    Implementar prompt al LLM aquí.
    """
    # Aquí iría tu prompt personalizado usando data y devolviendo nuevo dict.
    return data['params']

# --- Uso ---
# orig = cv2.imread('ruta.jpg')
# space = {'denoise': {'h':[5,10,15],'template_window':[3,7]}, 'contrast':{'alpha':[1,1.5,2],'beta':[0,10,20]}, ...}
# best = optimize_pipeline(orig, space, llm_adjust_callback)
