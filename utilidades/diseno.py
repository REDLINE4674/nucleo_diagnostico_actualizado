import tkinter as tk
from tkinter import ttk


COLORES = {
    "fondo": "#F0F2F5",
    "azul": "#1F4E79",
    "azul_presionado": "#163A5A",
    "azul_claro": "#E8EEF5",
    "azul_claro_presionado": "#D0DFEF",
    "azul_accion": "#5A8FC4",
    "gris_claro": "#E0E4E8",
    "gris_presionado": "#D0D5DA",
    "texto": "#333333",
    "texto_suave": "#666666",
    "texto_muted": "#888888",
    "texto_claro": "#DCE8F5",
    "verde": "#2E7D32",
    "verde_presionado": "#1B5E20",
    "blanco": "white",
}


FUENTES = {
    "compacta": ("Arial", 9),
    "compacta_negrita": ("Arial", 9, "bold"),
    "normal": ("Arial", 10),
    "normal_negrita": ("Arial", 10, "bold"),
    "mediana": ("Arial", 11),
    "mediana_negrita": ("Arial", 11, "bold"),
    "titulo_pequeno": ("Arial", 12, "bold"),
    "titulo_14": ("Arial", 14, "bold"),
    "titulo_16": ("Arial", 16, "bold"),
    "titulo_17": ("Arial", 17, "bold"),
    "titulo": ("Arial", 18, "bold"),
    "titulo_19": ("Arial", 19, "bold"),
    "marca": ("Arial", 22, "bold"),
    "marca_grande": ("Arial", 30, "bold"),
}


_ESTILOS_BOTON = {
    "principal": {
        "bg": COLORES["azul"], "fg": COLORES["blanco"],
        "relief": "flat", "font": FUENTES["normal_negrita"], "cursor": "hand2",
    },
    "secundario": {
        "bg": COLORES["azul_claro"], "fg": COLORES["azul"],
        "relief": "flat", "font": FUENTES["normal"], "cursor": "hand2",
    },
    "suave": {
        "bg": COLORES["azul_claro"], "fg": COLORES["texto"],
        "relief": "flat", "font": FUENTES["normal"], "cursor": "hand2",
    },
    "accion": {
        "bg": COLORES["azul_accion"], "fg": COLORES["blanco"],
        "relief": "flat", "font": FUENTES["normal_negrita"], "cursor": "hand2",
    },
    "neutro": {
        "bg": COLORES["gris_claro"], "fg": COLORES["texto"],
        "relief": "flat", "font": FUENTES["normal"], "cursor": "hand2",
    },
    "exito": {
        "bg": COLORES["verde"], "fg": COLORES["blanco"],
        "relief": "flat", "font": FUENTES["normal_negrita"], "cursor": "hand2",
    },
    "blanco": {
        "bg": COLORES["blanco"], "fg": COLORES["azul"],
        "relief": "flat", "font": FUENTES["normal_negrita"], "cursor": "hand2",
    },
}


_ESTILOS_ETIQUETA = {
    "encabezado": {
        "bg": COLORES["azul"], "fg": COLORES["blanco"], "font": FUENTES["titulo"],
    },
    "sobre_azul": {
        "bg": COLORES["azul"], "fg": COLORES["texto_claro"], "font": FUENTES["normal"],
    },
    "titulo": {
        "bg": COLORES["blanco"], "fg": COLORES["azul"], "font": FUENTES["titulo"],
    },
    "texto": {
        "bg": COLORES["blanco"], "fg": COLORES["texto"], "font": FUENTES["normal"],
    },
    "suave": {
        "bg": COLORES["blanco"], "fg": COLORES["texto_suave"], "font": FUENTES["normal"],
    },
    "tenue": {
        "bg": COLORES["blanco"], "fg": COLORES["texto_muted"], "font": FUENTES["normal"],
    },
}


def crear_etiqueta(parent, *, estilo="texto", **opciones):
    """Crea una etiqueta con colores y tipografia compartidos."""
    configuracion = _ESTILOS_ETIQUETA[estilo].copy()
    configuracion.update(opciones)
    return tk.Label(parent, **configuracion)


def crear_boton(parent, *, estilo="principal", **opciones):
    """Crea un boton con el estilo compartido y permite ajustes puntuales."""
    configuracion = _ESTILOS_BOTON[estilo].copy()
    configuracion.update(opciones)
    return tk.Button(parent, **configuracion)


_ESTILOS_MARCO = {
    "fondo": {"bg": COLORES["fondo"]},
    "superficie": {"bg": COLORES["blanco"]},
    "azul": {"bg": COLORES["azul"]},
    "tarjeta": {
        "bg": COLORES["blanco"],
        "relief": "solid",
        "borderwidth": 1,
    },
}


def crear_marco(parent, *, estilo="superficie", **opciones):
    """Crea un marco con uno de los fondos y bordes compartidos."""
    configuracion = _ESTILOS_MARCO[estilo].copy()
    configuracion.update(opciones)
    return tk.Frame(parent, **configuracion)


def crear_entrada(parent, **opciones):
    """Crea una entrada de texto con la tipografia y el borde comunes."""
    configuracion = {
        "font": FUENTES["normal"],
        "relief": "solid",
        "borderwidth": 1,
    }
    configuracion.update(opciones)
    return tk.Entry(parent, **configuracion)


def crear_combobox(parent, **opciones):
    """Crea un selector con la tipografia compartida."""
    configuracion = {"font": FUENTES["normal"]}
    configuracion.update(opciones)
    return ttk.Combobox(parent, **configuracion)



def crear_tabla_con_scroll(
    parent, *, columnas=(), horizontal=True, distribucion="grid", **opciones
):
    """Crea una tabla con scroll vertical y, si se solicita, horizontal."""
    opciones.setdefault("show", "headings")
    tabla = ttk.Treeview(parent, columns=columnas, **opciones)
    scroll_vertical = ttk.Scrollbar(
        parent,
        orient="vertical",
        command=tabla.yview
    )
    tabla.configure(yscrollcommand=scroll_vertical.set)

    if distribucion == "pack":
        tabla.pack(side="left", fill="both", expand=True)
        scroll_vertical.pack(side="right", fill="y")
        return tabla

    tabla.grid(row=0, column=0, sticky="nsew")
    scroll_vertical.grid(row=0, column=1, sticky="ns")
    if horizontal:
        scroll_horizontal = ttk.Scrollbar(
            parent,
            orient="horizontal",
            command=tabla.xview
        )
        tabla.configure(xscrollcommand=scroll_horizontal.set)
        scroll_horizontal.grid(row=1, column=0, sticky="ew")
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    return tabla



def crear_encabezado_seccion(
    parent, titulo, subtitulo, *, mostrar_contador=False
):
    """Crea el encabezado comun de una pagina y devuelve su contador opcional."""
    encabezado = crear_marco(parent, estilo="superficie")
    encabezado.pack(fill="x", padx=20, pady=15)
    informacion = crear_marco(encabezado, estilo="superficie")
    informacion.pack(side="left")
    crear_etiqueta(informacion, text=titulo, estilo="titulo").pack(anchor="w")
    crear_etiqueta(
        informacion,
        text=subtitulo,
        estilo="suave"
    ).pack(anchor="w", pady=(3, 0))

    contador = None
    if mostrar_contador:
        contador = crear_etiqueta(
            encabezado,
            text="Registros encontrados: 0",
            estilo="suave",
            font=FUENTES["normal_negrita"]
        )
        contador.pack(side="right")
    return encabezado, contador
