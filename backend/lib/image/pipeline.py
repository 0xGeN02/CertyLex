"""
    Generar el pipeline de preprocesamiento de imágenes.
"""

import cv2
import numpy as np
import pytesseract
from eth_hash.auto import keccak


def is_blurry(image, threshold=100):
    """
    Check if the image is blurry using the Laplacian variance method.
    Args:
        image (numpy.ndarray): The input image to check.
        threshold (float): The threshold for blurriness. Lower values indicate more blur.
    Returns:
        bool: True if the image is blurry, False otherwise.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold


def resize_image(image, width=1024):
    """
    Resize the image to a specified width while maintaining the aspect ratio.
    Args:
        image (numpy.ndarray): The input image to resize.
        width (int): The desired width of the resized image.
    Returns:
        numpy.ndarray: The resized image.
    """
    height = int(image.shape[0] * (width / image.shape[1]))
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


def normalize_image(image):
    """
    Normalize the image using CLAHE (Contrast Limited Adaptive Histogram Equalization).
    Args:
        image (numpy.ndarray): The input image to normalize.
    Returns:
        numpy.ndarray: The normalized image.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def correct_image_rotation(image):
    """
    Detect and correct the rotation of the image.
    Args:
        image (numpy.ndarray): The input image to check and rotate.
    Returns:
        numpy.ndarray: The rotated image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]

    # Correct for slight rotation
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated_image


def make_denoise(step_h=10, step_template_window_size=7):
    """
    Create a denoising function using Non-Local Means Denoising.
    Args:
        step_h (int): The filter strength. A larger value will remove noise better but will also remove more details.
        step_templateWindowSize (int): The size of the template patch. Must be odd.
    Returns:
        function: A function that takes an image and applies denoising.
    """
    def _denoise(image):
        return cv2.fastNlMeansDenoisingColored(image, None, step_h, step_h,
                                               step_template_window_size, 21)
    _denoise.__name__ = f"denoise_h{step_h}"
    return _denoise


def adjust_brightness_contrast(image, alpha=1.5, beta=0):
    """
    Adjust the brightness and contrast of the image.
    Args:
        image (numpy.ndarray): The input image to adjust.
        alpha (float): The contrast control.
        beta (int): The brightness control.
    Returns:
        numpy.ndarray: The image with adjusted brightness and contrast.
    """
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


def detect_edges(image):
    """
    Detect edges in the image using Canny edge detection.
    Args:
        image (numpy.ndarray): The input image.
    Returns:
        numpy.ndarray: The image with detected edges.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(gray, 100, 200)


def extract_text_from_image(image):
    """
    Extract text from the image using OCR.
    Args:
        image (numpy.ndarray): The input image.
    Returns:
        str: The extracted text from the image.
    """
    return pytesseract.image_to_string(image)


def auto_crop(image):
    """
    Crop the image automatically by detecting the edges and removing borders.
    Args:
        image (numpy.ndarray): The input image to crop.
    Returns:
        numpy.ndarray: The cropped image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(thresh > 0))
    x, y, w, h = cv2.boundingRect(coords)
    return image[y:y+h, x:x+w]


def generate_metadata(image, processed_image):
    """
    Generate metadata about the image processing steps.
    Args:
        image (numpy.ndarray): The original image.
        processed_image (numpy.ndarray): The processed image.
    Returns:
        dict: Metadata about the image.
    """
    return {
        'original_size': image.shape,
        'processed_size': processed_image.shape,
        'is_blurry': is_blurry(image)
    }


def keccak_image_hash(image, fmt='.png'):
    """
    Generate a keccak256 hash of the image.
    
    Args:
        image (numpy.ndarray): The input image to hash.
        fmt (str): The format to encode the image (e.g., '.png', '.jpg').
        
    Returns:
        str: The keccak256 hash of the image (bytes32hex).
    """
    # Encode the image to the specified format
    _, buf = cv2.imencode(fmt, image)
    if buf is None:
        raise ValueError("Failed to encode image")

    # Convert the encoded image to bytes
    image_bytes = buf.tobytes()

    # Compute the keccak256 hash
    return keccak(image_bytes).hex()


# Pipeline configuration
PIPELINE_STEPS = [
    correct_image_rotation,
    make_denoise(10, 7),
    lambda img: adjust_brightness_contrast(img, alpha=1.2, beta=10),
    resize_image,
    normalize_image,
    auto_crop
]

def process_image(image_path, steps=None):
    """
    Process an image using a series of image processing steps and return results.
    Args:
        image_path (str): The path to the input image.
        steps (list): A list of functions to apply to the image.
    Returns:
        dict: Contains original image, processed image, metadata, history, and hash.
    """
    orig = cv2.imread(image_path)
    if orig is None:
        raise ValueError(f"No se pudo cargar {image_path}")

    image = orig.copy()
    history = []
    metadata = {}
    if steps is None:
        steps = PIPELINE_STEPS

    for step in steps:
        try:
            prev = image.copy()
            image = step(image)
            metadata[step.__name__] = {
                "input_shape": prev.shape,
                "output_shape": image.shape
            }
            history.append(f"{step.__name__} applied")
        except Exception as e:
            history.append(f"{step.__name__} failed: {e}")

    # Compute final metadata and hash
    metadata.update(generate_metadata(orig, image))
    img_hash = keccak_image_hash(image)
    metadata["hash"] = img_hash
    history.append(f"hash computed: {img_hash[:8]}…")

    return {
        "original": orig,
        "processed": image,
        "metadata": metadata,
        "history": history
    }
