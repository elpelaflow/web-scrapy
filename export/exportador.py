import pandas as pd
import json
import os
import xml.etree.ElementTree as ET
from logs.debug_logger import logger

def exportar_csv(data: list[dict], ruta: str):
    df = pd.DataFrame(data)
    df.to_csv(ruta, index=False, encoding='utf-8')
    logger.info("Exportado a CSV: %s", ruta)

def exportar_excel(data: list[dict], ruta: str):
    df = pd.DataFrame(data)
    df.to_excel(ruta, index=False, engine='openpyxl')
    logger.info("Exportado a Excel: %s", ruta)

def exportar_json(data: list[dict], ruta: str):
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.info("Exportado a JSON: %s", ruta)

def exportar_xml(data: list[dict], ruta: str, root_name="Negocios", item_name="Negocio"):
    root = ET.Element(root_name)
    
    for item in data:
        item_elem = ET.SubElement(root, item_name)
        for key, value in item.items():
            child = ET.SubElement(item_elem, key)
            child.text = str(value) if value is not None else ""
    
    tree = ET.ElementTree(root)
    tree.write(ruta, encoding='utf-8', xml_declaration=True)
    logger.info("Exportado a XML: %s", ruta)

def exportar(data: list[dict], formato: str, ruta: str) -> str:
    """Exporta los datos al formato indicado en la carpeta dada."""
    os.makedirs(ruta, exist_ok=True)
    archivo = os.path.join(ruta, f"resultados.{formato}")

    if formato == "csv":
        exportar_csv(data, archivo)
    elif formato == "excel":
        exportar_excel(data, archivo)
    elif formato == "json":
        exportar_json(data, archivo)
    elif formato == "xml":
        exportar_xml(data, archivo)
    else:
        raise ValueError(f"Formato no soportado: {formato}")
    
    return archivo


def detectar_formato_y_exportar(data: list[dict], ruta: str) -> str:
    """Detecta el formato a partir de la extensión y exporta."""
    ext = os.path.splitext(ruta)[1].lower().lstrip(".")
    if ext:
        carpeta = os.path.dirname(ruta) or "."
        os.makedirs(carpeta, exist_ok=True)
        archivo = ruta
        if ext == "csv":
            exportar_csv(data, archivo)
        elif ext == "excel":
            exportar_excel(data, archivo)
        elif ext == "json":
            exportar_json(data, archivo)
        elif ext == "xml":
            exportar_xml(data, archivo)
        else:
            raise ValueError(f"Formato no soportado: {ext}")
        return archivo
    else:
        return exportar(data, "csv", ruta)
    