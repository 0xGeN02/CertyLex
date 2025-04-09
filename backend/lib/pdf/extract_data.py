import PyPDF2

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extrae todo el texto de un archivo PDF y lo devuelve como una cadena.
    
    Parámetros:
        file_path (str): Ruta al archivo PDF.
    
    Retorna:
        str: Todo el texto contenido en el PDF.
    """
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_by_pages(file_path: str) -> list[str]:
    """
    Extrae el texto de cada página de un PDF.
    
    Parámetros:
        file_path (str): Ruta al archivo PDF.
    
    Retorna:
        list[str]: Una lista donde cada elemento es el texto de una página.
    """
    pages_text = []
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            pages_text.append(page_text if page_text else "")
    return pages_text

# Ejemplo de uso:
if __name__ == "__main__":
    pdf_file = "/ruta/al/archivo.pdf"
    text = extract_text_from_pdf(pdf_file)
    print(text)
    pages_text = extract_text_by_pages(pdf_file)
    print(pages_text)
