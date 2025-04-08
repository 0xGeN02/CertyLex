"""
Módulo para descargar el sumario del BOE en formato JSON.
"""

import os
import json
import requests

def download_boe_sumario(fecha: str) -> bool:
    """
    Descarga el sumario del BOE para una fecha específica y lo guarda en formato JSON.
    """
    # Obtener el directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))

    #DIrectorio de gurdado de json de los boe
    boe_dir = os.path.join(current_dir, f"../../../data/boe/sumario/{fecha[:4]}") # Directorio de guardado de los JSON del BOE en subdirectorio por año

    # Crar el directorio si no existe
    os.makedirs(boe_dir, exist_ok=True)
    print(f"Directorio de guardado: {boe_dir}")

    # Configurar la solicitud
    url = f"https://boe.es/datosabiertos/api/boe/sumario/{fecha}" # Formato de fecha : AAAAmmdd (20240101)
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

    return True

if __name__ == "__main__":
    import datetime

    start_date = datetime.date(2010, 1, 1)
    end_date = datetime.date(2013, 12, 31)
    delta = datetime.timedelta(days=1)

    current = start_date
    while current <= end_date:
        FECHA = current.strftime("%Y%m%d")
        download_boe_sumario(FECHA)
        current += delta
