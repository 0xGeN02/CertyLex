"""
Generar el pipeline de preprocesamiento de imágenes con optimización de hiperparámetros asistida por LLM.
"""
# --- Importaciones ---

import random
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
    return cv2.Laplacian(gray, cv2.CV_64F).var() < threshold


def correct_image_rotation(image, **params):
    """
    Detect and correct rotation.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def make_denoise(h=10, template_window=7):
    """Factory de denoise con parámetros ajustables."""
    def _denoise(image):
        return cv2.fastNlMeansDenoisingColored(image, None, h, h, template_window, 21)
    _denoise.__name__ = f"denoise(h={h},tw={template_window})"
    _denoise.__params__ = {'h': h, 'template_window': template_window}
    return _denoise


def adjust_brightness_contrast(image, alpha=1.5, beta=0):
    """
    Ajusta brillo y contraste de la imagen.
    """
    out = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    adjust_brightness_contrast.__params__ = {'alpha': alpha, 'beta': beta}
    return out


def resize_image(image, width=1024):
    """
    Redimensiona la imagen manteniendo la relación de aspecto.
    """
    height = int(image.shape[0] * (width / image.shape[1]))
    out = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    resize_image.__params__ = {'width': width, 'height': height}
    return out


def normalize_image(image, clipLimit=2.0, tileGrid=(8,8)):
    """
    Normaliza la imagen usando CLAHE.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGrid)
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    out = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    normalize_image.__params__ = {'clipLimit': clipLimit, 'tileGrid': tileGrid}
    return out


def auto_crop(image, margin=0):
    """
    Recorta la imagen automáticamente eliminando bordes vacíos.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(th > 0))
    x, y, w, h = cv2.boundingRect(coords)
    x0, y0 = max(0, x - margin), max(0, y - margin)
    x1, y1 = min(image.shape[1], x + w + margin), min(image.shape[0], y + h + margin)
    auto_crop.__params__ = {'margin': margin}
    return image[y0:y1, x0:x1]


def keccak_image_hash(image, fmt='.png'):
    """
    Genera un hash Keccak de la imagen.
    """
    _, buf = cv2.imencode(fmt, image)
    return keccak(buf.tobytes()).hex()

# --- Construcción de pipeline dinámico ---

def named_step(fn, name):
    """
    Asigna un nombre a la función para identificarla en el pipeline.
    Se usa para la depuración y el ajuste de hiperparámetros.
    """
    fn.__step_name__ = name
    return fn

def build_pipeline(config):
    """
    Construye la lista de pasos del pipeline según:
      - config['use']: qué pasos activar (bool)
      - config['params']: hiperparámetros por paso
    Devuelve una lista de funciones aplicables con nombre accesible por .__step_name__
    """
    steps = []
    use = config.get("use", {})
    params = config.get("params", {})

    if use.get("rotate", True):
        steps.append(named_step(correct_image_rotation, "rotate"))

    if use.get("denoise", True):
        steps.append(named_step(make_denoise(**params.get('denoise', {})), "denoise"))

    if use.get("contrast", True):
        steps.append(named_step(
            lambda img: adjust_brightness_contrast(img, **params.get('contrast', {})),
            "contrast"
        ))

    if use.get("resize", True):
        steps.append(named_step(
            lambda img: resize_image(img, **params.get('resize', {})),
            "resize"
        ))

    if use.get("normalize", True):  # o 'clahe' si prefieres
        steps.append(named_step(
            lambda img: normalize_image(img, **params.get('normalize', {})),
            "normalize"
        ))

    if use.get("crop", True):
        steps.append(named_step(
            lambda img: auto_crop(img, **params.get('crop', {})),
            "crop"
        ))

    if use.get("hash", True):
        steps.append(named_step(
            lambda img: keccak_image_hash(img, **params.get('hash', {})),
            "hash"
        ))

    return steps

# --- Procesamineto de imagen ---

def process_image(image, steps):
    """
    Aplica los pasos del pipeline a una imagen y devuelve:
      - imagen procesada
      - historial con nombres y shape
    """
    history = []
    result = image.copy()

    for step in steps:
        name = getattr(step, '__step_name__', step.__name__)
        try:
            prev_shape = result.shape if isinstance(result, np.ndarray) else "n/a"
            result = step(result)
            new_shape = result.shape if isinstance(result, np.ndarray) else "n/a"
            history.append({
                "step": name,
                "status": "ok",
                "input_shape": prev_shape,
                "output_shape": new_shape
            })
        except Exception as e:
            history.append({
                "step": name,
                "status": "error",
                "error": str(e)
            })

    return result, history

# --- Evaluación de calidad ---

def evaluate_image_quality(orig, proc):
    """
    Retorna métricas de reducción de blur y ganancia en OCR.
    """
    b_orig = cv2.Laplacian(cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    b_proc = cv2.Laplacian(cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    text_orig = len(pytesseract.image_to_string(orig))
    text_proc = len(pytesseract.image_to_string(proc))
    return {
        'blur_reduction': b_proc - b_orig,
        'ocr_gain': text_proc - text_orig,
        'score': (b_proc - b_orig) + (text_proc - text_orig)
    }

# --- Optimización asistida ---

def optimize_pipeline(orig_image, param_space, llm_call, max_iter=3):
    """
    Optimiza hiperparámetros mediante muestreo y ajuste LLM.
    Devuelve el mejor resultado con historial y configuración.
    """
    best = {'score': -float('inf')}
    for _ in range(max_iter):
        # Randomly sample parameters
        current_params = {
            k: {sk: random.choice(v) for sk, v in sp.items()}
            for k, sp in param_space.items()
        }
        # Enable all steps initially
        config = {
            "use": dict.fromkeys(current_params.keys(), True),
            "params": current_params
        }
        steps = build_pipeline(config)
        img, history = process_image(orig_image, steps)
        metrics = evaluate_image_quality(orig_image, img if isinstance(img, np.ndarray) else None)

        # Get LLM-adjusted config
        new_config = llm_call({
            "orig": orig_image,
            "proc": img,
            "metrics": metrics,
            "params": current_params
        })
        new_steps = build_pipeline(new_config)
        new_img, new_history = process_image(orig_image, new_steps)
        new_metrics = evaluate_image_quality(orig_image, new_img if isinstance(new_img, np.ndarray) else None)

        # Update best
        if new_metrics['score'] > best.get('score', -float('inf')):
            best = {
                'image': new_img,
                'config': new_config,
                'metrics': new_metrics,
                'history': new_history,
                'score': new_metrics['score']
            }
    return best
