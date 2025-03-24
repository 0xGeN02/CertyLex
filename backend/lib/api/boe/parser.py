"""
Módulo para descargar el sumario del BOE en formato JSON.
"""

import os
import json
from datetime import datetime, timedelta
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
        filename = os.path.join(output_dir, f"{identificador}.{ext}")
        with open(filename, "wb") as f: # Binary write (wb) does not require encoding
            f.write(response.content)
        print(f"Descargado {ext.upper()} para {identificador}: {filename}")
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP {e.response.status_code} al descargar {url}")
    except requests.exceptions.Timeout:
        print(f"Timeout al descargar {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud de {url}: {e}")

def download_boe_documentos(json_filepath: str):
    """
    Lee el archivo JSON del sumario del BOE, extrae los documentos referenciados 
    y los descarga en la carpeta de salida organizada por año y fecha.
    
    Los documentos se descargan en formato HTML, XML y PDF (si están disponibles).
    
    Parámetros:
      json_filepath (str): Ruta completa al archivo JSON del sumario.
      output_base_dir (str): Carpeta base donde se guardarán los documentos descargados.
    """
    # Fecha de publicación (por ejemplo, "20150101")
    fecha_publicacion = json_filepath.rsplit("_", maxsplit=-1)[-1].replace(".json", "")

    # ./backend/data/boe/diario
    output_base_dir ="./backend/data/boe/diario"
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

                            # Descargar documento en formato HTML (deprecate to use XML form NLP and Machine Learning)
                            # url_html = item.get("url_html")
                            # if url_html:
                            #     html_output_dir = os.path.join(output_dir, "html")
                            #     os.makedirs(html_output_dir, exist_ok=True)
                            #     descargar_documento(url_html, "html", html_output_dir, identificador)
                            # Descargar documento en formato XML
                            url_xml = item.get("url_xml")
                            if url_xml:
                                xml_output_dir = os.path.join(output_dir, "xml")
                                os.makedirs(xml_output_dir, exist_ok=True)
                                descargar_documento(url_xml, "xml", xml_output_dir, identificador)
                            else:
                                print(f"No se encontró URL XML ni HTML para {identificador}")


def procesar_rango_fechas(start_date: str, end_date: str, base_path: str):
    """
    Procesa todos los archivos JSON en un rango de fechas y ejecuta la función download_boe_documentos.
    
    Parámetros:
        start_date (str): Fecha de inicio en formato YYYYMMDD.
        end_date (str): Fecha de fin en formato YYYYMMDD.
        base_path (str): Ruta base donde se encuentran los archivos JSON.
    """
    current_date = datetime.strptime(start_date, "%Y%m%d")
    end_date = datetime.strptime(end_date, "%Y%m%d")

    while current_date <= end_date:
        fecha_str = current_date.strftime("%Y%m%d")
        json_filepath = os.path.join(base_path, fecha_str[:4], f"BOE_sumario_{fecha_str}.json")

        if os.path.exists(json_filepath):
            print(f"Procesando archivo: {json_filepath}")
            download_boe_documentos(json_filepath)
        else:
            print(f"Archivo no encontrado: {json_filepath}")

        current_date += timedelta(days=1)

if __name__ == "__main__":
    # Ruta base donde se encuentran los archivos JSON
    BASE_PATH = "./backend/data/boe/sumario/"
    # Rango de fechas
    START_DATE = "20140101"
    END_DATE = "20250322"

    procesar_rango_fechas(START_DATE, END_DATE, BASE_PATH)
