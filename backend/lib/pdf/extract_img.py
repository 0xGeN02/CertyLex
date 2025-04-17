"""
Extrae imágenes de un archivo PDF y las guarda en un directorio especificado.
"""

import os
import fitz  # PyMuPDF

def extract_images_from_pdf(file_path: str, output_folder: str) -> None:
    """
    Extrae todas las imágenes de cada página de un PDF y las guarda en el directorio indicado.
    
    Parámetros:
        file_path (str): Ruta del archivo PDF.
        output_folder (str): Directorio donde se guardarán las imágenes extraídas.
    """
    # Crea el directorio de salida si no existe
    os.makedirs(output_folder, exist_ok=True)

    # Abrir el documento PDF
    doc = fitz.open(file_path)
    for page_number, page in enumerate(doc, start=1):
        image_list = page.get_images(full=True)
        print(f"Página {page_number} - {len(image_list)} imagen(es) encontrada(s).")
        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image.get("image")
            image_ext = base_image.get("ext")
            image_filename = os.path.join(output_folder, f"image_page{page_number}_{img_index}.{image_ext}")
            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)
            print(f"Imagen guardada: {image_filename}")

# Ejemplo de uso:
if __name__ == "__main__":
    PDF_FILE = "/ruta/al/archivo.pdf"
    OUTPUT_DIR = "/ruta/de/salida"
    extract_images_from_pdf(PDF_FILE, OUTPUT_DIR)
    