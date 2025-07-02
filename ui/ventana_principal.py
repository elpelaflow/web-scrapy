import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.ttk import Treeview
import pandas as pd
import json
from pathlib import Path
import threading
from scraper import ejecutar_scraper
from logs.solicitudes_log import registrar_log
from logs.debug_logger import logger
import yaml
import traceback

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scraper de Negocios")
        self.root.geometry("600x500")

        # Carpeta donde se guardarán los resultados
        self.export_folder = None

        self.config_path = Path(__file__).resolve().parent.parent / "config.yaml"
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self._original_proxies = self.config.get("proxies", [])
        self._original_user_agents = self.config.get("user_agents", [])

        data_path = Path(__file__).resolve().parent.parent / "data" / "provincias.json"
        with open(data_path, "r", encoding="utf-8") as f:
            self.paises_dict = json.load(f)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.busqueda_frame = ttk.Frame(self.notebook)
        self.historial_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.busqueda_frame, text="Buscar")
        self.notebook.add(self.historial_frame, text="Historial")

        # --- País ---
        tk.Label(self.busqueda_frame, text="País *").pack(pady=(10, 0))
        self.pais_var = tk.StringVar(value=list(self.paises_dict.keys())[0])
        self.pais_menu = ttk.Combobox(
            self.busqueda_frame,
            textvariable=self.pais_var,
            state="readonly",
            values=list(self.paises_dict.keys()),
        )
        self.pais_menu.pack()
        self.pais_menu.bind("<<ComboboxSelected>>", self.actualizar_provincias)

        # --- Provincia ---
        tk.Label(self.busqueda_frame, text="Provincia").pack(pady=(10, 0))
        self.provincia_var = tk.StringVar()
        self.provincia_menu = ttk.Combobox(self.busqueda_frame, textvariable=self.provincia_var, state="readonly")
        self.provincia_menu.pack()

        # --- Localidad ---
        tk.Label(self.busqueda_frame, text="Localidad").pack(pady=(10, 0))
        self.localidad_entry = tk.Entry(self.busqueda_frame)
        self.localidad_entry.pack()

        # --- Categoría de Negocio ---
        tk.Label(self.busqueda_frame, text="Categoría de negocio *").pack(pady=(10, 0))
        self.categoria_entry = tk.Entry(self.busqueda_frame)
        self.categoria_entry.pack()

        # --- Palabra clave de producto ---
        tk.Label(self.busqueda_frame, text="Palabra clave de producto *").pack(pady=(10, 0))
        self.palabra_entry = tk.Entry(self.busqueda_frame)
        self.palabra_entry.pack()

        # --- Límite máximo ---
        tk.Label(self.busqueda_frame, text="Límite máximo de resultados").pack(pady=(10, 0))
        self.limite_entry = tk.Entry(self.busqueda_frame)
        self.limite_entry.insert(0, "100")
        self.limite_entry.pack()

        # --- Formato de salida ---
        tk.Label(self.busqueda_frame, text="Formato de exportación").pack(pady=(10, 0))
        self.formato_var = tk.StringVar(value="csv")
        self.formato_menu = ttk.Combobox(
            self.busqueda_frame,
            textvariable=self.formato_var,
            state="readonly",
            values=["csv", "excel", "json", "xml"],
        )
        self.formato_menu.pack()

         # --- Opciones avanzadas ---
        self.headless_var = tk.BooleanVar(value=self.config.get("headless", True))
        tk.Checkbutton(
            self.busqueda_frame,
            text="Headless mode",
            variable=self.headless_var,
            command=self.guardar_config,
        ).pack()

        self.proxy_var = tk.BooleanVar(value=bool(self.config.get("proxies")))
        tk.Checkbutton(
            self.busqueda_frame,
            text="Rotación de proxies",
            variable=self.proxy_var,
            command=self.guardar_config,
        ).pack()

        self.ua_var = tk.BooleanVar(value=bool(self.config.get("user_agents")))
        tk.Checkbutton(
            self.busqueda_frame,
            text="Cambio de user-agent",
            variable=self.ua_var,
            command=self.guardar_config,
        ).pack()

        # --- Carpeta de salida ---
        self.ruta_var = tk.StringVar()
        tk.Button(
            self.busqueda_frame,
            text="Seleccionar carpeta...",
            command=self.seleccionar_carpeta,
        ).pack(pady=(10, 0))
        ttk.Label(self.busqueda_frame, textvariable=self.ruta_var).pack()

        # --- Botón de búsqueda ---
        self.buscar_btn = tk.Button(
            self.busqueda_frame, text="Iniciar búsqueda", command=self.iniciar_busqueda_thread
        )
        self.buscar_btn.pack(pady=20)

        # --- Barra de progreso ---
        self.progress = ttk.Progressbar(self.busqueda_frame, length=400, mode="determinate")
        self.progress.pack(pady=(0, 10))

        # --- Área de log ---
        self.log_text = tk.Text(self.busqueda_frame, height=8, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.crear_historial()
        self.actualizar_provincias()

    def iniciar_busqueda_thread(self):
        self.buscar_btn.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")
        threading.Thread(target=self.iniciar_busqueda, daemon=True).start()

    def progress_callback(self, item, cantidad, limite):
        self.root.after(0, self._update_progress, cantidad, limite)

    def _update_progress(self, cantidad, limite):
        self.progress["maximum"] = limite
        self.progress["value"] = cantidad
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"Ficha {cantidad}/{limite} completada\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.export_folder = carpeta
            self.ruta_var.set(carpeta)

    def guardar_config(self):
        self.config["headless"] = self.headless_var.get()
        self.config["proxies"] = self._original_proxies if self.proxy_var.get() else []
        self.config["user_agents"] = (
            self._original_user_agents if self.ua_var.get() else []
        )
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(self.config, f, allow_unicode=True)
        except Exception:
            logger.exception("Error al guardar configuracion")

    def actualizar_provincias(self, event=None):
        pais = self.pais_var.get()
        provincias = self.paises_dict.get(pais, [])
        self.provincia_menu["values"] = [""] + provincias
        self.provincia_var.set("")

    def crear_historial(self):
        self.history_columns = [
            "Fecha",
            "País",
            "Provincia",
            "Localidad",
            "Categoría",
            "Keyword",
            "Resultados",
            "Duración",
        ]
        self.tree = Treeview(self.historial_frame, columns=self.history_columns, show="headings")
        for col in self.history_columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        scrollbar = ttk.Scrollbar(self.historial_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        tk.Button(self.historial_frame, text="Refrescar", command=self.cargar_historial).pack(pady=5)
        self.cargar_historial()

    def cargar_historial(self):
        ruta_log = Path("logs/solicitudes_log.csv")
        if ruta_log.exists():
            try:
                df = pd.read_csv(ruta_log)
            except pd.errors.ParserError:
                df = pd.read_csv(ruta_log, engine="python", on_bad_lines="skip")
        else:
            df = pd.DataFrame(columns=self.history_columns)
        self.tree.delete(*self.tree.get_children())
        for _, fila in df.iterrows():
            self.tree.insert(
                "",
                "end",
                values=[
                    fila.get("Fecha y Hora", ""),
                    fila.get("País", ""),
                    fila.get("Provincia", ""),
                    fila.get("Localidad", ""),
                    fila.get("Categoría", ""),
                    fila.get("Palabra Clave", ""),
                    fila.get("Cantidad de Resultados", ""),
                    fila.get("Runtime Seconds", ""),
                ],
            )

    def mostrar_error(self, exc: Exception):
        logger.error("Fallo en la UI", exc_info=exc)
        top = tk.Toplevel(self.root)
        top.title("Error")
        tk.Label(top, text=str(exc), fg="red").pack(padx=10, pady=10)

        detalle = tk.Text(top, height=10)
        detalle.insert(tk.END, traceback.format_exc())
        detalle.config(state="disabled")

        def toggle():
            if detalle.winfo_viewable():
                detalle.pack_forget()
                btn.config(text="Ver detalles")
            else:
                detalle.pack(fill="both", expand=True, padx=10, pady=(0, 10))
                btn.config(text="Ocultar detalles")

        btn = tk.Button(top, text="Ver detalles", command=toggle)
        btn.pack(pady=(0, 10))
        tk.Button(top, text="Cerrar", command=top.destroy).pack(pady=(0, 10))   
    
    def iniciar_busqueda(self):
        pais = self.pais_var.get().strip()
        provincia = self.provincia_var.get().strip()
        localidad = self.localidad_entry.get().strip()
        categoria = self.categoria_entry.get().strip()
        palabra = self.palabra_entry.get().strip()
        limite = self.limite_entry.get().strip()

        if not pais or not categoria or not palabra:
            messagebox.showerror("Error", "Los campos país, categoría y palabra clave son obligatorios.")
            return

        try:
            limite = int(limite)
        except ValueError:
            messagebox.showerror("Error", "El límite debe ser un número entero.")
            return

        parametros = {
            "pais": pais,
            "provincia": provincia,
            "localidad": localidad,
            "categoria": categoria,
            "palabra": palabra,
            "limite": limite,
            "formato": self.formato_var.get(),
        }
        
        print("Parámetros de búsqueda:", parametros)
        
        ruta = getattr(self, "export_folder", None)
        if not ruta:
            messagebox.showwarning("Error", "Seleccioná primero la carpeta de destino")
            return
        parametros["ruta_salida"] = ruta

        try:
            archivo, cantidad = ejecutar_scraper(parametros, callback=self.progress_callback)
            messagebox.showinfo(
                "Éxito", f"Se guardaron {cantidad} resultados en:\n{archivo}"
            )
        except Exception as e:
            messagebox.showerror("Error durante el scraping", str(e))
        finally:
            self.buscar_btn.config(state=tk.NORMAL)


def iniciar_ui():
    """Punto de entrada para la interfaz gráfica."""
    root = tk.Tk()
    app = ScraperApp(root)
    root.mainloop()


if __name__ == "__main__":
    iniciar_ui()