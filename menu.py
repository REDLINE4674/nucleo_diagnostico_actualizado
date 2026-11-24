import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk
from citas import (
    abrir_consulta_citas,
    abrir_formulario_cita,
    mostrar_consulta_citas
)
from conexion import obtener_tablas
from consultas import mostrar_datos
from consultas_citas import obtener_doctor_por_usuario
from consultas_medicas import (
    abrir_ventana_consulta_medica,
    obtener_consultas_doctor,
    obtener_pacientes_doctor
)
from insertar import abrir_ventana_insertar


def mostrar_menu(ventana, conexion, usuario, rol, al_cerrar_sesion):

    ventana.title("Nucleo De Diagnostico")
    ventana.configure(bg="#F0F2F5")

    rol_str = str(rol)
    es_administrador = rol_str == "1"
    es_empleado = rol_str == "2"
    es_doctor = rol_str == "3"

    perfil = (
        "Administrador" if es_administrador
        else "Empleado" if es_empleado
        else "Doctor" if es_doctor
        else "Rol no definido"
    )

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

    def es_tabla_pacientes(nombre_tabla):
        nombre_normalizado = str(nombre_tabla).strip().strip('"').lower()
        return nombre_normalizado in ("paciente", "pacientes")

    def es_tabla_citas(nombre_tabla):
        nombre_normalizado = str(nombre_tabla).strip().strip('"').lower()
        return nombre_normalizado in ("cita", "citas")

    def es_tabla_consultas(nombre_tabla):
        nombre_normalizado = str(nombre_tabla).strip().strip('"').lower()
        return nombre_normalizado in ("consulta", "consultas")

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

    def descripcion_seccion(nombre_tabla):
        descripciones = {
            "doctor": "Consulta la información de los médicos registrados.",
            "empleado": "Consulta la información del personal registrado.",
            "paciente": (
                "Consulta los pacientes que tienen cita agendada contigo."
                if es_doctor
                else "Consulta la información de los pacientes registrados."
            ),
            "consulta": "Consulta el historial clínico y registra diagnósticos y recetas.",
            "consultas": "Consulta el historial clínico y registra diagnósticos y recetas.",
            "medicamento": "Consulta el catálogo de medicamentos registrados.",
            "usuarios": "Consulta las cuentas y roles de usuario."
        }
        nombre_normalizado = str(nombre_tabla).strip().strip('"').lower()
        return descripciones.get(
            nombre_normalizado,
            "Consulta los registros de esta sección."
        )

    def texto_boton_insertar(nombre_tabla):
        etiquetas = {
            "doctor": "Registrar doctor",
            "doctores": "Registrar doctor",
            "empleado": "Registrar empleado",
            "empleados": "Registrar empleado",
            "paciente": "Registrar paciente",
            "pacientes": "Registrar paciente",
            "medicamento": "Registrar medicamento",
            "medicamentos": "Registrar medicamento",
            "usuario": "Nuevo usuario",
            "usuarios": "Nuevo usuario"
        }
        nombre_normalizado = str(nombre_tabla).strip().strip('"').lower()
        return etiquetas.get(nombre_normalizado, "Nuevo registro")

    barra_superior = tk.Frame(ventana, bg="#1F4E79")
    barra_superior.pack(fill="x", padx=12, pady=(12, 0))

    tk.Label(
        barra_superior,
        text=f"Bienvenido  {usuario}  ({perfil})",
        font=("Arial", 12, "bold"),
        bg="#1F4E79",
        fg="white"
    ).pack(side="left", padx=15, pady=10)

    tk.Button(
        barra_superior,
        text="Cerrar sesión",
        command=al_cerrar_sesion,
        bg="white",
        fg="#1F4E79",
        relief="flat",
        font=("Arial", 10, "bold"),
        cursor="hand2"
    ).pack(side="right", padx=10, pady=5)

    # CONTENEDOR PRINCIPAL

    contenido = tk.Frame(ventana, bg="#F0F2F5")
    contenido.pack(fill="both", expand=True)

# MENU LATERAL

    menu = tk.Frame(
        contenido,
        bg="white",
        width=210,
        relief="solid",
        borderwidth=1
    )

    menu.pack(
        side="left",
        fill="y",
        padx=(12, 6),
        pady=12
    )

    menu.pack_propagate(False)

    tk.Label(
        menu,
        text="CONSULTAS GENERALES",
        font=("Arial", 12, "bold"),
        bg="white",
        fg="#1F4E79"
    ).pack(pady=(15, 10))

    ttk.Separator(
        menu,
        orient="horizontal"
    ).pack(fill="x", padx=12, pady=5)

    # Canvas con scroll para que quepan todas las tablas
    canvas_menu = tk.Canvas(menu, bg="white", highlightthickness=0)
    scroll_menu = ttk.Scrollbar(menu, orient="vertical", command=canvas_menu.yview)

    contenedor_botones = tk.Frame(canvas_menu, bg="white")
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
    tk.Button(
        contenedor_botones,
        text="Citas",
        command=lambda: mostrar_seccion_citas(),
        width=20,
        height=1,
        bg="#E8EEF5",
        fg="#333333",
        activebackground="#D0DFEF",
        relief="flat",
        font=("Arial", 10),
        cursor="hand2"
    ).pack(pady=4, padx=4, ipady=4)

    # PANEL DE CONTENIDO

    panel = tk.Frame(
        contenido,
        bg="white",
        relief="solid",
        borderwidth=1
    )

    panel.pack(
        side="right",
        fill="both",
        expand=True,
        padx=(6, 12),
        pady=12
    )

    tabla_seleccionada = {"nombre": None}

    def limpiar_panel():
        for widget in panel.winfo_children():
            widget.destroy()

    # MENU PRINCIPAL

    def mostrar_inicio():

        boton_regresar.pack_forget()
        tabla_seleccionada["nombre"] = None

        limpiar_panel()

        inicio = tk.Frame(
            panel,
            bg="white"
        )

        inicio.pack(
            fill="both",
            expand=True
        )

        try:
            ruta_imagen = Path(__file__).resolve().parent / "imagenes" / "nd.png"
            imagen = Image.open(ruta_imagen)
            imagen = imagen.resize((160, 160))

            logo = ImageTk.PhotoImage(imagen)

            etiqueta_imagen = tk.Label(
                inicio,
                image=logo,
                bg="white"
            )

            etiqueta_imagen.image = logo
            etiqueta_imagen.pack(pady=(50, 15))

        except Exception:

            tk.Label(
                inicio,
                text="NÚCLEO",
                font=("Arial", 30, "bold"),
                fg="#1F4E79",
                bg="white"
            ).pack(pady=(70, 15))

        tk.Label(
            inicio,
            text=f"Usuario: {usuario}",
            font=("Arial", 21, "bold"),
            bg="white",
            fg="#333333"
        ).pack(pady=10)

        tk.Label(
            inicio,
            text=f"Perfil: {perfil}",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#1F4E79"
        ).pack(pady=(0, 10))

        tk.Label(
            inicio,
            text="Bienvenido al sistema de administración de datos.",
            font=("Arial", 11),
            bg="white",
            fg="#666666"
        ).pack(pady=15)

        tk.Label(
            inicio,
            text="Selecciona una opción del menú lateral para comenzar.",
            font=("Arial", 10),
            bg="white",
            fg="#888888"
        ).pack(pady=5)

    boton_regresar = tk.Button(
        barra_superior,
        text="Regresar al menú",
        command=mostrar_inicio,
        bg="#E8EEF5",
        fg="#1F4E79",
        relief="flat",
        font=("Arial", 10),
        cursor="hand2"
    )

    def mostrar_seccion_citas():
        if not boton_regresar.winfo_manager():
            boton_regresar.pack(side="right", padx=(0, 10), pady=5)

        # Si es doctor y no está vinculado, usar -1 para no mostrar citas de otros médicos
        filtro_doctor = (
            (id_doctor_logueado if id_doctor_logueado is not None else -1)
            if es_doctor
            else None
        )
        tabla_seleccionada["nombre"] = None
        limpiar_panel()

        encabezado_citas = tk.Frame(panel, bg="white")
        encabezado_citas.pack(fill="x", padx=20, pady=15)

        informacion_citas = tk.Frame(encabezado_citas, bg="white")
        informacion_citas.pack(side="left")

        tk.Label(
            informacion_citas,
            text="Citas",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#1F4E79"
        ).pack(anchor="w")

        subtitulo_citas = (
            "Consulta tus citas médicas agendadas."
            if es_doctor
            else "Genera, consulta y actualiza citas médicas."
        )
        tk.Label(
            informacion_citas,
            text=subtitulo_citas,
            font=("Arial", 10),
            bg="white",
            fg="#666666"
        ).pack(anchor="w", pady=(3, 0))

        contador_citas = tk.Label(
            encabezado_citas,
            text="Registros encontrados: 0",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#666666"
        )
        contador_citas.pack(side="right")

        botones_citas = tk.Frame(panel, bg="white")
        botones_citas.pack(fill="x", padx=20, pady=15)

        area_resultados_citas = tk.Frame(panel, bg="white")
        area_resultados_citas.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        filtro_doctor = id_doctor_logueado if es_doctor else None

        tk.Button(
            botones_citas,
            text="Consultar citas",
            command=lambda: mostrar_consulta_citas(
                area_resultados_citas,
                conexion,
                contador_citas,
                id_doctor=filtro_doctor
            ),
            width=20,
            bg="#5A8FC4",
            fg="white",
            relief="flat",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(side="left", padx=5)

        # Solo Empleado o Administrador pueden generar o modificar citas
        if es_empleado or es_administrador:
            tk.Button(
                botones_citas,
                text="Generar cita",
                command=lambda: abrir_formulario_cita(ventana, conexion),
                width=20,
                bg="#1F4E79",
                fg="white",
                relief="flat",
                font=("Arial", 10, "bold"),
                cursor="hand2"
            ).pack(side="right", padx=5)

            tk.Button(
                botones_citas,
                text="Actualizar cita",
                command=lambda: abrir_consulta_citas(
                    ventana,
                    conexion,
                    permitir_actualizacion=True
                ),
                width=20,
                bg="#1F4E79",
                fg="white",
                relief="flat",
                font=("Arial", 10, "bold"),
                cursor="hand2"
            ).pack(side="right", padx=5)

    # VISTA DE TABLAS

    def seleccionar_tabla(nombre):

        if not tabla_permitida(nombre):
            messagebox.showwarning(
                "Acceso restringido",
                "Tu perfil no tiene permisos para acceder a esta sección.",
                parent=ventana
            )
            return

        if not boton_regresar.winfo_manager():
            boton_regresar.pack(side="right", padx=(0, 10), pady=5)

        tabla_seleccionada["nombre"] = nombre

        limpiar_panel()

        encabezado_tabla = tk.Frame(
            panel,
            bg="white"
        )

        encabezado_tabla.pack(
            fill="x",
            padx=20,
            pady=15
        )

        informacion_seccion = tk.Frame(encabezado_tabla, bg="white")
        informacion_seccion.pack(side="left")

        titulo_tabla = tk.Label(
            informacion_seccion,
            text=str(nombre).strip().capitalize(),
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#1F4E79"
        )
        titulo_tabla.pack(anchor="w")

        tk.Label(
            informacion_seccion,
            text=descripcion_seccion(nombre),
            font=("Arial", 10),
            bg="white",
            fg="#666666"
        ).pack(anchor="w", pady=(3, 0))

        contador_registros = tk.Label(
            encabezado_tabla,
            text="Registros encontrados: 0",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#666666"
        )
        contador_registros.pack(side="right")

        vista_registros = {"tabla": None}

        def asegurar_treeview():
            if vista_registros["tabla"] is None:
                contenedor_tabla = tk.Frame(panel, bg="white")
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
            nombre_actual = tabla_seleccionada["nombre"]
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
            bg="white"
        )

        botones.pack(
            fill="x",
            padx=20,
            pady=15
        )

        tk.Button(
            botones,
            text="Consultar registros",
            command=actualizar,
            width=20,
            bg="#5A8FC4",
            fg="white",
            relief="flat",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(side="left", padx=5)

        # Doctor en Consultas: botón para diagnóstico, medicamentos y receta PDF
        if es_doctor and es_tabla_consultas(nombre):
            tk.Button(
                botones,
                text="Nueva consulta / Receta",
                command=lambda: abrir_ventana_consulta_medica(
                    ventana,
                    conexion,
                    id_doctor_logueado,
                    nombre_doctor_logueado,
                    al_guardar=lambda: actualizar(mostrar_si_oculto=True)
                ),
                width=24,
                bg="#1F4E79",
                fg="white",
                relief="flat",
                font=("Arial", 10, "bold"),
                cursor="hand2"
            ).pack(side="right")

        # Insertar registro genérico (Administrador o Empleado en Pacientes)
        elif es_administrador or (
            es_empleado and es_tabla_pacientes(nombre)
        ):
            if not es_tabla_citas(nombre):
                tk.Button(
                    botones,
                    text=texto_boton_insertar(nombre),
                    command=lambda: abrir_ventana_insertar(
                        ventana,
                        conexion,
                        nombre,
                        lambda: actualizar(mostrar_si_oculto=False)
                    ),
                    width=20,
                    bg="#1F4E79",
                    fg="white",
                    relief="flat",
                    font=("Arial", 10, "bold"),
                    cursor="hand2"
                ).pack(side="right")

    # CARGAR TABLAS EN EL MENÚ LATERAL

    try:

        tablas = obtener_tablas(conexion)

        if not tablas:

            tk.Label(
                contenedor_botones,
                text="No hay tablas disponibles",
                bg="white",
                fg="gray",
                font=("Arial", 9)
            ).pack(pady=10)

        for fila in tablas:

            nombre = fila[0]

            if es_tabla_citas(nombre):
                continue

            if not tabla_permitida(nombre):
                continue

            tk.Button(
                contenedor_botones,
                text=nombre.capitalize(),
                command=lambda n=nombre: seleccionar_tabla(n),
                width=20,
                height=1,
                bg="#E8EEF5",
                fg="#333333",
                activebackground="#D0DFEF",
                relief="flat",
                font=("Arial", 10),
                cursor="hand2"
            ).pack(pady=4, padx=4, ipady=4)

    except Exception as error:

        messagebox.showerror(
            "Error",
            "No se pudieron obtener las tablas.\n\n" + str(error)
        )

    mostrar_inicio()
