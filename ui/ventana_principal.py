import tkinter as tk
from tkinter import ttk, messagebox
import threading
from scraper import ejecutar_scraper
from logs.solicitudes_log import registrar_log

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scraper de Negocios")
        self.root.geometry("500x450")

        # --- País ---
        tk.Label(root, text="País *").pack(pady=(10, 0))
        self.pais_var = tk.StringVar(value="Argentina")
        pais_menu = ttk.Combobox(root, textvariable=self.pais_var, state="readonly")
        pais_menu['values'] = ["Argentina"]
        pais_menu.pack()

        # --- Provincia ---
        tk.Label(root, text="Provincia").pack(pady=(10, 0))
        self.provincia_var = tk.StringVar()
        self.provincia_menu = ttk.Combobox(root, textvariable=self.provincia_var)
        self.provincia_menu['values'] = ["", "Buenos Aires", "Córdoba", "Santa Fe", "Mendoza"]
        self.provincia_menu.pack()

        # --- Localidad ---
        tk.Label(root, text="Localidad").pack(pady=(10, 0))
        self.localidad_entry = tk.Entry(root)
        self.localidad_entry.pack()

        # --- Categoría de Negocio ---
        tk.Label(root, text="Categoría de negocio *").pack(pady=(10, 0))
        self.categoria_entry = tk.Entry(root)
        self.categoria_entry.pack()

        # --- Palabra clave de producto ---
        tk.Label(root, text="Palabra clave de producto *").pack(pady=(10, 0))
        self.palabra_entry = tk.Entry(root)
        self.palabra_entry.pack()

        # --- Límite máximo ---
        tk.Label(root, text="Límite máximo de resultados").pack(pady=(10, 0))
        self.limite_entry = tk.Entry(root)
        self.limite_entry.insert(0, "100")
        self.limite_entry.pack()

        # --- Botón de búsqueda ---
        buscar_btn = tk.Button(root, text="Iniciar búsqueda", command=self.iniciar_busqueda_thread)
        buscar_btn.pack(pady=20)

    def iniciar_busqueda_thread(self):
        threading.Thread(target=self.iniciar_busqueda).start()

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
        }

        try:
            archivo, cantidad = ejecutar_scraper(parametros)
            registrar_log(pais, provincia, localidad, categoria, palabra, limite, archivo, cantidad)
            messagebox.showinfo("Éxito", f"Se guardaron {cantidad} resultados en:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error durante el scraping", str(e))


def iniciar_ui():
    """Punto de entrada para la interfaz gráfica."""
    root = tk.Tk()
    app = ScraperApp(root)
    root.mainloop()


if __name__ == "__main__":
    iniciar_ui()