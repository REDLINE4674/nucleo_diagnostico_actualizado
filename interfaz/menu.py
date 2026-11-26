import tkinter as tk
from tkinter import ttk, messagebox

from operaciones_sql.consultas import obtener_tablas
from operaciones_sql.citas import obtener_doctor_por_usuario
from secciones.citas import mostrar_pagina_citas
from secciones.inicio import mostrar_inicio as mostrar_pagina_inicio
from secciones.registros import (
    es_tabla_citas,
    es_tabla_consultas,
    es_tabla_pacientes,
    mostrar_pagina_registros
)
from utilidades.roles import obtener_nombre_perfil
from utilidades.diseno import COLORES, FUENTES, crear_boton, crear_etiqueta, crear_marco


def mostrar_menu(ventana, conexion, usuario, rol, al_cerrar_sesion):
    ventana.title("Nucleo De Diagnostico")
    ventana.configure(bg=COLORES["fondo"])

    rol_str = str(rol)
    es_administrador = rol_str == "1"
    es_empleado = rol_str == "2"
    es_doctor = rol_str == "3"

    perfil = obtener_nombre_perfil(rol)

    doctor_actual = None
    if es_doctor:
        try:
            doctor_actual = obtener_doctor_por_usuario(conexion, usuario)
        except Exception as error:
            messagebox.showerror(
                "Error de médico",
                f"No se pudo vincular el usuario con un médico:\n{error}",
                parent=ventana
            )
        if doctor_actual is None:
            messagebox.showwarning(
                "Médico no vinculado",
                f"No se encontró un registro en la tabla 'doctor' con el nombre '{usuario}'.\n"
                "Verifica que el nombre de usuario coincida con el del médico.",
                parent=ventana
            )

    id_doctor_logueado = doctor_actual[0] if doctor_actual else None
    nombre_doctor_logueado = doctor_actual[1] if doctor_actual else usuario

    def tabla_permitida(nombre_tabla):
        if es_administrador:
            return True
        if es_empleado:
            return es_tabla_pacientes(nombre_tabla)
        if es_doctor:
            return (
                es_tabla_pacientes(nombre_tabla)
                or es_tabla_consultas(nombre_tabla)
            )
        return False

    barra_superior = crear_marco(ventana, estilo="azul")
    barra_superior.pack(fill="x", padx=12, pady=(12, 0))

    crear_etiqueta(barra_superior, text=f'Bienvenido  {usuario}  ({perfil})', estilo="encabezado", font=FUENTES['titulo_pequeno']).pack(side="left", padx=15, pady=10)

    crear_boton(
        barra_superior,
        text="Cerrar sesi\u00f3n",
        command=lambda: al_cerrar_sesion(usuario),
        estilo="blanco"
    ).pack(side="right", padx=10, pady=5)

    # CONTENEDOR PRINCIPAL

    contenido = crear_marco(ventana, estilo="fondo")
    contenido.pack(fill="both", expand=True)

# MENU LATERAL

    menu = crear_marco(contenido, estilo="tarjeta", width=210)

    menu.pack(
        side="left",
        fill="y",
        padx=(12, 6),
        pady=12
    )

    menu.pack_propagate(False)

    crear_etiqueta(menu, text='CONSULTAS GENERALES', estilo="titulo", font=FUENTES['titulo_pequeno']).pack(pady=(15, 10))

    ttk.Separator(
        menu,
        orient="horizontal"
    ).pack(fill="x", padx=12, pady=5)

    # Canvas con scroll para que quepan todas las tablas
    canvas_menu = tk.Canvas(menu, bg=COLORES["blanco"], highlightthickness=0)
    scroll_menu = ttk.Scrollbar(menu, orient="vertical", command=canvas_menu.yview)

    contenedor_botones = crear_marco(canvas_menu, estilo="superficie")
    ventana_menu = canvas_menu.create_window((0, 0), window=contenedor_botones, anchor="nw")

    canvas_menu.configure(yscrollcommand=scroll_menu.set)
    canvas_menu.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
    scroll_menu.pack(side="right", fill="y", pady=6)

    contenedor_botones.bind(
        "<Configure>",
        lambda e: canvas_menu.configure(scrollregion=canvas_menu.bbox("all"))
    )
    canvas_menu.bind(
        "<Configure>",
        lambda e: canvas_menu.itemconfigure(ventana_menu, width=e.width)
    )

    # Acceso a las funciones de citas (Empleado, Doctor y Administrador)
    crear_boton(contenedor_botones, text='Citas', command=lambda: mostrar_seccion_citas(), estilo="suave", width=20, height=1, activebackground=COLORES["azul_claro_presionado"]).pack(pady=4, padx=4, ipady=4)

    # PANEL DE CONTENIDO

    panel = crear_marco(contenido, estilo="tarjeta")

    panel.pack(
        side="right",
        fill="both",
        expand=True,
        padx=(6, 12),
        pady=12
    )

    def limpiar_panel():
        for widget in panel.winfo_children():
            widget.destroy()

    # MENU PRINCIPAL

    def mostrar_inicio():
        boton_regresar.pack_forget()
        limpiar_panel()
        mostrar_pagina_inicio(panel, usuario, perfil)

    boton_regresar = crear_boton(barra_superior, text='Regresar al menú', command=mostrar_inicio, estilo="secundario")

    def mostrar_seccion_citas():
        if not boton_regresar.winfo_manager():
            boton_regresar.pack(side="right", padx=(0, 10), pady=5)
        limpiar_panel()
        mostrar_pagina_citas(
            panel,
            ventana,
            conexion,
            es_doctor,
            es_empleado,
            es_administrador,
            id_doctor_logueado
        )

    # VISTA DE TABLAS

    def seleccionar_tabla(nombre):
        if not tabla_permitida(nombre):
            messagebox.showwarning(
                "Acceso restringido",
                "Tu perfil no tiene permisos para acceder a esta secci\u00f3n.",
                parent=ventana
            )
            return

        if not boton_regresar.winfo_manager():
            boton_regresar.pack(side="right", padx=(0, 10), pady=5)
        limpiar_panel()
        mostrar_pagina_registros(
            panel,
            ventana,
            conexion,
            nombre,
            es_administrador,
            es_empleado,
            es_doctor,
            id_doctor_logueado,
            nombre_doctor_logueado
        )

    # CARGAR TABLAS EN EL MENÚ LATERAL

    try:

        tablas = obtener_tablas(conexion)

        if not tablas:

            tk.Label(
                contenedor_botones,
                text="No hay tablas disponibles",
                bg=COLORES["blanco"],
                fg="gray",
                font=FUENTES["compacta"]
            ).pack(pady=10)

        for fila in tablas:

            nombre = fila[0]

            if es_tabla_citas(nombre):
                continue

            if not tabla_permitida(nombre):
                continue

            crear_boton(contenedor_botones, text=nombre.capitalize(), command=lambda n=nombre: seleccionar_tabla(n), estilo="suave", width=20, height=1, activebackground=COLORES["azul_claro_presionado"]).pack(pady=4, padx=4, ipady=4)

    except Exception as error:

        messagebox.showerror(
            "Error",
            "No se pudieron obtener las tablas.\n\n" + str(error)
        )

    mostrar_inicio()
