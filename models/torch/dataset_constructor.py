import os
import xml.etree.ElementTree as ET
import json
from datetime import datetime

def list_xml_files_in_range(
    base_dir: str,
    start_date: str,
    end_date: str,
    date_format: str = "%d/%m/%Y"
):
    start = datetime.strptime(start_date, date_format)
    end = datetime.strptime(end_date, date_format)
    xml_paths = []
    for year in os.listdir(base_dir):
        year_path = os.path.join(base_dir, year)
        if not os.path.isdir(year_path) or not year.isdigit():
            continue
        for date_folder in os.listdir(year_path):
            date_path = os.path.join(year_path, date_folder)
            try:
                folder_date = datetime.strptime(date_folder, "%Y%m%d")
            except ValueError:
                continue
            if start <= folder_date <= end:
                xml_dir = os.path.join(date_path, 'xml')
                if os.path.isdir(xml_dir):
                    for fn in os.listdir(xml_dir):
                        if fn.endswith('.xml'):
                            xml_paths.append(os.path.join(xml_dir, fn))
    return sorted(xml_paths)

def extract_boe_pair(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    title = root.findtext('.//titulo') or ''
    materias = [m.text for m in root.findall('.//materias/materia') if m.text]
    alertas = [a.text for a in root.findall('.//alertas/alerta') if a.text]
    paragraphs = [p.text for p in root.findall('.//texto//p') if p.text]
    body = "\n".join(paragraphs)
    input_text = f"<DOCUMENTO>\nTITULO: {title}\nMATERIAS: {', '.join(materias)}\nALERTAS: {', '.join(alertas)}\nTEXTO:\n{body}\n</DOCUMENTO>"
    output_text = f"<RESUMEN>\n{title}\n</RESUMEN>\n<PUNTOS_CLAVE>\n{'; '.join(materias + alertas)}\n</PUNTOS_CLAVE>"
    return input_text, output_text

def make_boe_dataset_range(base_dir, start_date, end_date, output_jsonl):
    files = list_xml_files_in_range(base_dir, start_date, end_date)
    pairs = []
    for xml_path in files:
        try:
            inp, out = extract_boe_pair(xml_path)
            pairs.append({'input': inp, 'output': out})
        except Exception as e:
            print(f"Error en {xml_path}: {e}")
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + '\n')
    print(f"Guardado {len(pairs)} pares en {output_jsonl}")

if __name__ == "__main__":
    base_dir = "/home/xgen0/CertyChain/CertyLex/backend/data/boe/diario"
    start_date = "01/01/2024"
    end_date = "01/01/2025"
    output_jsonl = "boe_dataset.jsonl"
    make_boe_dataset_range(base_dir, start_date, end_date, output_jsonl)