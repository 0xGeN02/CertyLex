"""
Módulo para descargar el sumario del BOE en formato JSON.
"""

import os
import json
import requests
from datetime import datetime

def download_boe_sumario(fecha: str):
    """
    Descarga el sumario del BOE para una fecha específica y lo guarda en formato JSON.
    """
    # Obtener el directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))

    #DIrectorio de gurdado de json de los boe
    boe_dir = os.path.join(current_dir, "../boe")

    # Crar el directorio si no existe
    os.makedirs(boe_dir, exist_ok=True)
    print(f"Directorio de guardado: {boe_dir}")

    # Configurar la solicitud
    url = f"https://boe.es/datosabiertos/api/boe/sumario/{fecha}"
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Guardar el JSON
        filename = f"{boe_dir}/BOE_sumario_{fecha}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)

        print(f"Sumario de {fecha} guardado en {filename}")

    except requests.exceptions.HTTPError as e:
        print(f"Error {e.response.status_code} para fecha {fecha}")
    except requests.exceptions.Timeout:
        print(f"Timeout para la solicitud a {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")
    except json.JSONDecodeError:
        print(f"Error al decodificar la respuesta JSON para {fecha}")
    except OSError as e:
        print(f"Error al guardar el archivo: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    FECHA = "20240101"
    download_boe_sumario(FECHA)
