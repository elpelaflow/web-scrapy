import argparse
from scraper import ejecutar_scraper


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ejecuta el scraper de negocios desde la linea de comandos"
    )
    parser.add_argument("--pais", required=True, help="País a buscar")
    parser.add_argument("--provincia", default="", help="Provincia")
    parser.add_argument("--localidad", default="", help="Localidad")
    parser.add_argument("--categoria", required=True, help="Categoría de negocio")
    parser.add_argument("--palabra", required=True, help="Palabra clave de producto")
    parser.add_argument(
        "--limite", type=int, default=100, help="Máximo de resultados a obtener"
    )
    parser.add_argument(
        "--formato",
        choices=["csv", "excel", "json", "xml"],
        default="csv",
        help="Formato de salida",
    )
    parser.add_argument(
        "--ruta-salida",
        default=None,
        help="Ruta del archivo de salida (incluye nombre y extensión)",
    )

    args = parser.parse_args()
    params = {
        "pais": args.pais,
        "provincia": args.provincia,
        "localidad": args.localidad,
        "categoria": args.categoria,
        "palabra": args.palabra,
        "limite": args.limite,
        "formato": args.formato,
    }
    if args.ruta_salida:
        params["ruta_salida"] = args.ruta_salida

    archivo, cantidad = ejecutar_scraper(params)
    print(f"Se guardaron {cantidad} resultados en: {archivo}")


if __name__ == "__main__":
    main()