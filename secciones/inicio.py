from pathlib import Path
import tkinter as tk
from PIL import Image, ImageTk
from utilidades.diseno import COLORES, FUENTES, crear_etiqueta


def mostrar_inicio(panel, usuario, perfil):
    inicio = tk.Frame(panel, bg=COLORES["blanco"])
    inicio.pack(fill="both", expand=True)

    try:
        ruta_imagen = Path(__file__).resolve().parents[1] / "imagenes" / "nd.png"
        imagen = Image.open(ruta_imagen).resize((160, 160))
        logo = ImageTk.PhotoImage(imagen)
        etiqueta_imagen = tk.Label(inicio, image=logo, bg=COLORES["blanco"])
        etiqueta_imagen.image = logo
        etiqueta_imagen.pack(pady=(50, 15))
    except Exception:
        crear_etiqueta(inicio, text='NÚCLEO', estilo="titulo", font=FUENTES['marca_grande']).pack(pady=(70, 15))

    crear_etiqueta(inicio, text=f'Usuario: {usuario}', estilo="texto", font=('Arial', 21, 'bold')).pack(pady=10)
    crear_etiqueta(inicio, text=f'Perfil: {perfil}', estilo="titulo", font=FUENTES['mediana_negrita']).pack(pady=(0, 10))
    crear_etiqueta(inicio, text='Bienvenido al sistema de administración de datos.', estilo="suave", font=FUENTES['mediana']).pack(pady=15)
    crear_etiqueta(inicio, text='Selecciona una opción del menú lateral para comenzar.', estilo="tenue", font=FUENTES['normal']).pack(pady=5)
