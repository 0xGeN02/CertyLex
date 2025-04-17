"""
    Generar el pipeline de preprocesamiento de imágenes.
"""

import cv2

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

def img_pipeline(image):
    """
    Process the image through a series of transformations.
    Args:
        image (numpy.ndarray): The input image to process.
    Returns:
        numpy.ndarray: The processed image.
    """
    # Check if the image is blurry
    if is_blurry(image):
        print("Image is blurry, skipping processing.")
        return image

    # Resize the image
    resized_image = resize_image(image)

    # Normalize the image
    normalized_image = normalize_image(resized_image)

    return normalized_image

def process_image(image_path):
    """
    Process the image from the given path.
    Args:
        image_path (str): The path to the image file.
    Returns:
        numpy.ndarray: The processed image.
    """
    # Read the image
    image = cv2.imread(image_path)

    # Check if the image was loaded successfully
    if image is None:
        raise ValueError(f"Image at {image_path} could not be loaded.")

    # Process the image
    processed_image = img_pipeline(image)

    return processed_image

# Example usage
if __name__ == "__main__":
    IMAGE_PATH = "path/to/your/image.jpg"
    processd_image = process_image(IMAGE_PATH)

    # Display the processed image
    cv2.imshow("Processed Image", processd_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
