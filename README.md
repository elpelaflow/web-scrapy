# WebScraper de Negocios

Aplicación para obtener datos de comercios desde Google Maps de forma sencilla. Permite filtrar por país, provincia, localidad y palabra clave de producto. Los resultados pueden exportarse a CSV, Excel, JSON o XML.

## Instalación

```bash
git clone https://github.com/elpelaflow/web-scrapy.git
cd web-scrapy
python -m venv .venv
source .venv/bin/activate  # En Windows usar .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso rápido

Ejecuta la aplicación con:

```bash
python main.py
```

Se abrirá una ventana donde deberás ingresar el país, la categoría y la palabra clave que desees buscar. Opcionalmente puedes indicar provincia, localidad y el número máximo de resultados.

Cuando la búsqueda finalice se mostrará la ubicación del archivo exportado junto con la cantidad de registros.

## Uso por línea de comandos

Además de la interfaz gráfica puedes ejecutar el scraper desde la terminal. Los
parámetros disponibles son equivalentes a los de la ventana de la aplicación.

```bash
python cli.py --pais Argentina --categoria "Restaurantes" \
    --palabra pizza --limite 50 --formato csv --ruta-salida salida.csv
```

El argumento `--formato` acepta `csv`, `excel`, `json` o `xml`. Con `--ruta-salida`
puedes definir la ubicación y nombre del archivo generado.

## Flujo de trabajo del scraper

1. **`navegador.py`** configura el *webdriver* de Selenium.
2. **`recolector.py`** realiza la navegación en Google Maps y obtiene las URLs de las fichas.
3. **`extractor.py`** extrae la información de cada negocio abierto en el navegador.
4. **`controlador.py`** orquesta todo el proceso y delega la exportación al módulo **`export/exportador.py`**.
5. Los datos se guardan en la carpeta `data/resultados/` con el formato elegido.

## Ejemplo de interfaz

La aplicación utiliza Tkinter por lo que se abre una ventana similar a la siguiente:

![Captura de ejemplo](docs/captura_ejemplo.png)

En ella se completan los parámetros y se inicia la recolección.

## Historial

La pestaña de historial carga el archivo `logs/solicitudes_log.csv` omitiendo
automáticamente las líneas corruptas que pudieran existir.

## Uso ético

Utiliza esta herramienta únicamente para fines legales y con el permiso de los sitios que scrapees. El uso indebido puede violar los términos de servicio de las páginas y la legislación vigente.