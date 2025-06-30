import pandas as pd
import json
import os
import xml.etree.ElementTree as ET

def exportar_csv(data: list[dict], ruta: str):
    df = pd.DataFrame(data)
    df.to_csv(ruta, index=False, encoding='utf-8')
    print(f"[INFO] Exportado a CSV: {ruta}")

def exportar_excel(data: list[dict], ruta: str):
    df = pd.DataFrame(data)
    df.to_excel(ruta, index=False, engine='openpyxl')
    print(f"[INFO] Exportado a Excel: {ruta}")

def exportar_json(data: list[dict], ruta: str):
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"[INFO] Exportado a JSON: {ruta}")

def exportar_xml(data: list[dict], ruta: str, root_name="Negocios", item_name="Negocio"):
    root = ET.Element(root_name)
    
    for item in data:
        item_elem = ET.SubElement(root, item_name)
        for key, value in item.items():
            child = ET.SubElement(item_elem, key)
            child.text = str(value) if value is not None else ""
    
    tree = ET.ElementTree(root)
    tree.write(ruta, encoding='utf-8', xml_declaration=True)
    print(f"[INFO] Exportado a XML: {ruta}")

def exportar(data: list[dict], formato: str, ruta_salida: str):
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    
    if formato == "csv":
        exportar_csv(data, ruta_salida)
    elif formato == "excel":
        exportar_excel(data, ruta_salida)
    elif formato == "json":
        exportar_json(data, ruta_salida)
    elif formato == "xml":
        exportar_xml(data, ruta_salida)
    else:
        raise ValueError(f"Formato no soportado: {formato}")
