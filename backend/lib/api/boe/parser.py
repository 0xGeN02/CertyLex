"""
Módulo para descargar el sumario del BOE en formato JSON.
"""

import os
import json
import requests

# Función auxiliar para descargar un documento dado su URL y extensión
def descargar_documento(url: str , ext: str, output_dir: str, identificador: str) -> None:
    """
    Descarga un documento desde una URL y lo guarda en el directorio especificado.
    Parámetros:
        url (str): URL del documento a descargar.
        ext (str): Extensión del documento (html, xml, pdf).
        output_dir (str): Directorio donde se guardará el documento.
        identificador (str): Identificador del documento.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Se guarda el contenido en modo binario
        filename = os.path.join(output_dir, f"{identificador}_{ext}.{ext}")
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Descargado {ext.upper()} para {identificador}: {filename}")
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP {e.response.status_code} al descargar {url}")
    except requests.exceptions.Timeout:
        print(f"Timeout al descargar {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud de {url}: {e}")

def download_boe_documentos(json_filepath: str, fecha_publicacion: str):
    """
    Lee el archivo JSON del sumario del BOE, extrae los documentos referenciados 
    y los descarga en la carpeta de salida organizada por año y fecha.
    
    Los documentos se descargan en formato HTML, XML y PDF (si están disponibles).
    
    Parámetros:
      json_filepath (str): Ruta completa al archivo JSON del sumario.
      output_base_dir (str): Carpeta base donde se guardarán los documentos descargados.
    """
    # ./backend/data/boe/diario
    output_base_dir ="../../../data/boe/diario"
    # Crear el directorio de salida: output_base_dir/{year}/{fecha_publicacion}/
    output_dir = os.path.join(output_base_dir, fecha_publicacion[:4], fecha_publicacion)

    os.makedirs(output_dir, exist_ok=True)
    print(f"Creando directorio de salida: {output_dir}")

    # Leer el JSON
    try:
        with open(json_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error al leer {json_filepath}: {e}")
        return

    # Obtener la fecha de publicación (por ejemplo, "20150101") del JSON
    fecha_publicacion = data.get("data", {}).get("sumario", {}).get("metadatos", {}).get("fecha_publicacion")
    if not fecha_publicacion:
        print(f"No se encontró 'fecha_publicacion' en {json_filepath}")
        return

    # Recorrer la estructura del sumario para extraer las URL de cada documento
    diarios = data.get("data", {}).get("sumario", {}).get("diario", [])
    if not isinstance(diarios, list):
        diarios = [diarios]

    for diario in diarios:
        secciones = diario.get("seccion", [])
        if not isinstance(secciones, list):
            secciones = [secciones]
        for seccion in secciones:
            departamentos = seccion.get("departamento")
            if departamentos:
                if not isinstance(departamentos, list):
                    departamentos = [departamentos]
                for dept in departamentos:
                    # Los epígrafes pueden estar anidados en 'texto' o directamente en 'epigrafe'
                    if "texto" in dept:
                        epigrafes = dept["texto"].get("epigrafe", [])
                    else:
                        epigrafes = dept.get("epigrafe", [])
                    if not isinstance(epigrafes, list):
                        epigrafes = [epigrafes]
                    for epigrafe in epigrafes:
                        items = epigrafe.get("item")
                        if not items:
                            continue
                        if not isinstance(items, list):
                            items = [items]
                        for item in items:
                            identificador = item.get("identificador", "sin_id")

                            # Descargar documento en formato HTML
                            url_html = item.get("url_html")
                            if url_html:
                                descargar_documento(url_html, "html", output_dir, identificador)
                            # Descargar documento en formato XML
                            url_xml = item.get("url_xml")
                            if url_xml:
                                descargar_documento(url_xml, "xml", output_dir, identificador)
                            else:
                                print(f"No se encontró URL XML ni HTML para {identificador}")


if __name__ == "__main__":
    # Ejemplo de uso: procesar un archivo JSON concreto
    JSON_FILE = "../../../data/boe/sumario/2015/BOE_sumario_20150101.json"
    FECHA_PUBLICACION = JSON_FILE.rsplit("_", maxsplit="-1")[-1]
    download_boe_documentos(JSON_FILE, FECHA_PUBLICACION)
