import os
import zipfile

EXCLUDE_DIRS = {'.git', '__pycache__', '.venv'}
EXCLUDE_EXTS = {'.pyc', '.pyo', '.zip'}
EXCLUDE_FILES = {'zip_proyecto.py'}


def debe_incluir(ruta: str) -> bool:
    """Determina si un archivo o carpeta debe añadirse al zip."""
    partes = ruta.split(os.sep)
    for parte in partes:
        if parte in EXCLUDE_DIRS or parte.startswith('.git'):
            return False
    nombre = os.path.basename(ruta)
    if nombre in EXCLUDE_FILES:
        return False
    _, ext = os.path.splitext(nombre)
    if ext in EXCLUDE_EXTS:
        return False
    return True


def crear_zip(nombre_zip: str = 'web-scrapy.zip') -> None:
    """Crea un zip del proyecto excluyendo archivos innecesarios."""
    raiz = os.path.dirname(os.path.abspath(__file__))
    with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for carpeta, subcarpetas, archivos in os.walk(raiz):
            subcarpetas[:] = [d for d in subcarpetas if debe_incluir(os.path.join(carpeta, d))]
            for archivo in archivos:
                ruta_completa = os.path.join(carpeta, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, raiz)
                if debe_incluir(ruta_relativa):
                    zipf.write(ruta_completa, ruta_relativa)


if __name__ == '__main__':
    crear_zip()