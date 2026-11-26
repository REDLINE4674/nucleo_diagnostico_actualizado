import tkinter as tk
from tkinter import ttk, messagebox

from operaciones_sql.consultas import consultar_registros
from operaciones_sql.consultas_medicas import (
    obtener_consultas_doctor,
    obtener_pacientes_doctor
)
from secciones.formulario_registro import abrir_ventana_insertar
from secciones.diagnosticos import abrir_ventana_consulta_medica
from utilidades.diseno import COLORES, FUENTES, crear_boton, crear_etiqueta


def es_tabla_pacientes(nombre_tabla):
    nombre_normalizado = str(nombre_tabla).strip().strip('"').lower()
    return nombre_normalizado in ("paciente", "pacientes")


def es_tabla_citas(nombre_tabla):
    nombre_normalizado = str(nombre_tabla).strip().strip('"').lower()
    return nombre_normalizado in ("cita", "citas")


def es_tabla_consultas(nombre_tabla):
    nombre_normalizado = str(nombre_tabla).strip().strip('"').lower()
    return nombre_normalizado in ("consulta", "consultas")


def descripcion_seccion(nombre_tabla, es_doctor):
    descripciones = {
        "doctor": "Consulta la informacion de los medicos registrados.",
        "empleado": "Consulta la informacion del personal registrado.",
        "paciente": (
            "Consulta los pacientes que tienen cita agendada contigo."
            if es_doctor
            else "Consulta la informacion de los pacientes registrados."
        ),
        "consulta": "Consulta el historial clinico y registra diagnosticos y recetas.",
        "consultas": "Consulta el historial clinico y registra diagnosticos y recetas.",
        "medicamento": "Consulta el catalogo de medicamentos registrados.",
        "usuarios": "Consulta las cuentas y roles de usuario."
    }
    nombre_normalizado = str(nombre_tabla).strip().strip('"').lower()
    return descripciones.get(
        nombre_normalizado,
        "Consulta los registros de esta seccion."
    )

def texto_boton_insertar(nombre_tabla):
    etiquetas = {
        "doctor": "Registrar doctor", "doctores": "Registrar doctor",
        "empleado": "Registrar empleado", "empleados": "Registrar empleado",
        "paciente": "Registrar paciente", "pacientes": "Registrar paciente",
        "medicamento": "Registrar medicamento", "medicamentos": "Registrar medicamento",
        "usuario": "Nuevo usuario", "usuarios": "Nuevo usuario"
    }
    nombre_normalizado = str(nombre_tabla).strip().strip('"').lower()
    return etiquetas.get(nombre_normalizado, "Nuevo registro")


def mostrar_datos(conexion, tabla_visual, titulo, nombre_tabla):
    try:
        columnas, registros = consultar_registros(conexion, nombre_tabla)
        titulo.config(text=nombre_tabla.capitalize())
        tabla_visual.delete(*tabla_visual.get_children())
        tabla_visual["columns"] = columnas
        for columna in columnas:
            tabla_visual.heading(columna, text=columna)
            tabla_visual.column(columna, width=220 if columna.lower() == "diagnostico" else 120)
        for registro in registros:
            tabla_visual.insert("", "end", values=registro)
        return len(registros)
    except Exception as error:
        messagebox.showerror(
            "Error",
            "No se pudieron consultar los registros.\n\n" + str(error)
        )
        return 0


def mostrar_pagina_registros(
    panel, ventana, conexion, nombre, es_administrador, es_empleado,
    es_doctor, id_doctor_logueado, nombre_doctor_logueado
):
    encabezado_tabla = tk.Frame(
        panel,
        bg=COLORES["blanco"]
    )

    encabezado_tabla.pack(
        fill="x",
        padx=20,
        pady=15
    )

    informacion_seccion = tk.Frame(encabezado_tabla, bg=COLORES["blanco"])
    informacion_seccion.pack(side="left")

    titulo_tabla = crear_etiqueta(informacion_seccion, text=str(nombre).strip().capitalize(), estilo="titulo", font=FUENTES['titulo'])
    titulo_tabla.pack(anchor="w")

    crear_etiqueta(informacion_seccion, text=descripcion_seccion(nombre, es_doctor), estilo="suave", font=FUENTES['normal']).pack(anchor="w", pady=(3, 0))

    contador_registros = crear_etiqueta(encabezado_tabla, text='Registros encontrados: 0', estilo="suave", font=FUENTES['normal_negrita'])
    contador_registros.pack(side="right")

    vista_registros = {"tabla": None}

    def asegurar_treeview():
        if vista_registros["tabla"] is None:
            contenedor_tabla = tk.Frame(panel, bg=COLORES["blanco"])
            contenedor_tabla.pack(
                fill="both",
                expand=True,
                padx=20,
                pady=10
            )

            tabla_visual = ttk.Treeview(
                contenedor_tabla,
                show="headings"
            )
            scroll_vertical = ttk.Scrollbar(
                contenedor_tabla,
                orient="vertical",
                command=tabla_visual.yview
            )
            scroll_horizontal = ttk.Scrollbar(
                contenedor_tabla,
                orient="horizontal",
                command=tabla_visual.xview
            )

            tabla_visual.configure(
                yscrollcommand=scroll_vertical.set,
                xscrollcommand=scroll_horizontal.set
            )
            tabla_visual.grid(row=0, column=0, sticky="nsew")
            scroll_vertical.grid(row=0, column=1, sticky="ns")
            scroll_horizontal.grid(row=1, column=0, sticky="ew")
            contenedor_tabla.grid_rowconfigure(0, weight=1)
            contenedor_tabla.grid_columnconfigure(0, weight=1)
            vista_registros["tabla"] = tabla_visual

        return vista_registros["tabla"]

    def poblar_treeview(tabla_visual, columnas, registros):
        tabla_visual.delete(*tabla_visual.get_children())
        tabla_visual["columns"] = columnas
        for col in columnas:
            tabla_visual.heading(col, text=col)
            tabla_visual.column(
                col,
                width=240 if col.lower() == "diagnostico" else 120
            )
        for reg in registros:
            tabla_visual.insert("", "end", values=reg)

    def actualizar(mostrar_si_oculto=True):
        nombre_actual = nombre
        if nombre_actual is None:
            return 0

        if vista_registros["tabla"] is None and not mostrar_si_oculto:
            return 0

        tabla_visual = asegurar_treeview()

        try:
            # Doctor consultando sus pacientes con cita
            if es_doctor and es_tabla_pacientes(nombre_actual):
                if id_doctor_logueado is None:
                    poblar_treeview(tabla_visual, [], [])
                    contador_registros.config(text="Registros encontrados: 0")
                    return 0
                columnas, registros = obtener_pacientes_doctor(
                    conexion,
                    id_doctor_logueado
                )
                poblar_treeview(tabla_visual, columnas, registros)
                contador_registros.config(
                    text=f"Registros encontrados: {len(registros)}"
                )
                return len(registros)

            # Doctor consultando sus consultas médicas
            if es_doctor and es_tabla_consultas(nombre_actual):
                columnas, registros = obtener_consultas_doctor(
                    conexion,
                    id_doctor_logueado
                )
                poblar_treeview(tabla_visual, columnas, registros)
                contador_registros.config(
                    text=f"Registros encontrados: {len(registros)}"
                )
                return len(registros)

            cantidad = mostrar_datos(
                conexion,
                tabla_visual,
                titulo_tabla,
                nombre_actual
            )
            contador_registros.config(
                text=f"Registros encontrados: {cantidad}"
            )
            return cantidad

        except Exception as error:
            messagebox.showerror(
                "Error",
                "No se pudieron consultar los registros.\n\n" + str(error),
                parent=ventana
            )
            return 0

    # BOTONES INFERIORES

    botones = tk.Frame(
        panel,
        bg=COLORES["blanco"]
    )

    botones.pack(
        fill="x",
        padx=20,
        pady=15
    )

    crear_boton(botones, text='Consultar registros', command=actualizar, estilo="accion", width=20).pack(side="left", padx=5)

    # Doctor en Consultas: botón para diagnóstico, medicamentos y receta PDF
    if es_doctor and es_tabla_consultas(nombre):
        crear_boton(botones, text='Nueva consulta / Receta', command=lambda: abrir_ventana_consulta_medica(ventana, conexion, id_doctor_logueado, nombre_doctor_logueado, al_guardar=lambda: actualizar(mostrar_si_oculto=True)), estilo="principal", width=24).pack(side="right")

    # Insertar registro genérico (Administrador o Empleado en Pacientes)
    elif es_administrador or (
        es_empleado and es_tabla_pacientes(nombre)
    ):
        if not es_tabla_citas(nombre):
            crear_boton(botones, text=texto_boton_insertar(nombre), command=lambda: abrir_ventana_insertar(ventana, conexion, nombre, lambda: actualizar(mostrar_si_oculto=False)), estilo="principal", width=20).pack(side="right")
