from pathlib import Path
import tkinter as tk
from PIL import Image, ImageTk
from utilidades.diseno import COLORES, FUENTES, crear_etiqueta, crear_marco


RUTA_LOGOTIPO = Path(__file__).resolve().parents[1] / "imagenes" / "nd.png"
TAMANO_LOGOTIPO = (160, 160)


def mostrar_inicio(panel, usuario, perfil):
    inicio = crear_marco(panel, estilo="superficie")
    inicio.pack(fill="both", expand=True)

    try:
        with Image.open(RUTA_LOGOTIPO) as imagen_original:
            imagen = imagen_original.convert("RGBA")
            resampling = getattr(Image, "Resampling", Image).LANCZOS
            imagen.thumbnail(TAMANO_LOGOTIPO, resampling)
            logo = ImageTk.PhotoImage(imagen, master=inicio)

        etiqueta_imagen = tk.Label(
            inicio,
            image=logo,
            bg=COLORES["blanco"]
        )
        etiqueta_imagen.image = logo
        etiqueta_imagen.pack(pady=(50, 15))
    except (OSError, tk.TclError) as error:
        print(f"No se pudo cargar el logotipo {RUTA_LOGOTIPO}: {error}")
        crear_etiqueta(
            inicio,
            text="N\u00daCLEO",
            estilo="titulo",
            font=FUENTES["marca_grande"]
        ).pack(pady=(70, 15))

    crear_etiqueta(inicio, text=f'Usuario: {usuario}', estilo="texto", font=('Arial', 21, 'bold')).pack(pady=10)
    crear_etiqueta(inicio, text=f'Perfil: {perfil}', estilo="titulo", font=FUENTES['mediana_negrita']).pack(pady=(0, 10))
    crear_etiqueta(inicio, text='Bienvenido al sistema de administración de datos.', estilo="suave", font=FUENTES['mediana']).pack(pady=15)
    crear_etiqueta(inicio, text='Selecciona una opción del menú lateral para comenzar.', estilo="tenue").pack(pady=5)
