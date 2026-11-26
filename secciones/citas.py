import calendar
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

from operaciones_sql.citas import (
    CitaDuplicadaError,
    obtener_pacientes,
    obtener_medicos,
    obtener_horarios_disponibles,
    registrar_cita,
    obtener_citas,
    obtener_cita,
    actualizar_cita
)
from utilidades.diseno import COLORES, FUENTES, crear_boton, crear_etiqueta, crear_tabla_con_scroll, crear_marco, crear_entrada, crear_combobox, crear_encabezado_seccion


def abrir_formulario_cita(
    ventana,
    conexion,
    al_guardar=None,
    id_cita=None
):
    nueva = tk.Toplevel(ventana)

    nueva.title("Actualizar cita" if id_cita is not None else "Generar cita")
    nueva.geometry("900x500")
    nueva.minsize(750, 430)
    nueva.configure(bg=COLORES["fondo"])

    nueva.transient(ventana)

    cita_edicion = {"id": None}
    pacientes = []
    medicos = []

    def obtener_id_seleccionado(combo, registros):
        indice = combo.current()
        if indice < 0 or indice >= len(registros):
            return None
        return registros[indice][0]

    # Encabezado

    encabezado = crear_marco(nueva, estilo="azul", height=75)

    encabezado.pack(fill="x")
    encabezado.pack_propagate(False)

    titulo_encabezado = crear_etiqueta(encabezado, text='ACTUALIZAR CITA' if id_cita is not None else 'GENERAR CITA', estilo="encabezado", font=FUENTES['titulo_19'])
    titulo_encabezado.pack(anchor="w", padx=25, pady=(15, 2))

    crear_etiqueta(encabezado, text='Modifica el médico, la fecha o el horario.' if id_cita is not None else 'Programa una cita médica.', estilo="sobre_azul").pack(anchor="w", padx=25)

    def regresar_menu():
        nueva.destroy()

    crear_boton(encabezado, text='Regresar al menú', command=regresar_menu, estilo="secundario", activebackground=COLORES["azul_claro_presionado"], font=('Arial', 9, 'bold')).place(
        relx=0.98,
        rely=0.5,
        anchor="e"
    )

    # Contenedor principal

    principal = crear_marco(nueva, estilo="fondo")

    principal.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=15
    )

    # Formulario

    formulario = crear_marco(principal, estilo="tarjeta")

    formulario.pack(
        fill="x",
        pady=(0, 12)
    )

    crear_etiqueta(formulario, text='Datos de la cita', estilo="titulo", font=FUENTES['titulo_14']).pack(anchor="w", padx=20, pady=(15, 10))

    campos = crear_marco(formulario, estilo="superficie")

    campos.pack(
        fill="x",
        padx=20,
        pady=(0, 15)
    )

    campos.grid_columnconfigure(0, weight=1)
    campos.grid_columnconfigure(1, weight=1)

    # Pacientes

    crear_etiqueta(campos, text='Paciente', estilo="texto", font=FUENTES['normal_negrita']).grid(row=0, column=0, sticky="w", padx=5, pady=5)

    combo_paciente = crear_combobox(campos, state='readonly')

    combo_paciente.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=5,
        pady=(0, 12)
    )

    # Doctores

    crear_etiqueta(campos, text='Médico', estilo="texto", font=FUENTES['normal_negrita']).grid(row=0, column=1, sticky="w", padx=5, pady=5)

    combo_medico = crear_combobox(campos, state='readonly')

    combo_medico.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=5,
        pady=(0, 12)
    )

    # Fecha

    crear_etiqueta(campos, text='Fecha (AAAA-MM-DD)', estilo="texto", font=FUENTES['normal_negrita']).grid(row=2, column=0, sticky="w", padx=5, pady=5)

    marco_fecha = crear_marco(campos, estilo="superficie")
    marco_fecha.grid(
        row=3,
        column=0,
        sticky="ew",
        padx=5,
        pady=(0, 12)
    )
    marco_fecha.grid_columnconfigure(0, weight=1)

    entrada_fecha = crear_entrada(marco_fecha)
    entrada_fecha.grid(row=0, column=0, sticky="ew", ipady=6)

    entrada_fecha.insert(0, date.today().isoformat())

    # Horario

    crear_etiqueta(campos, text='Horario disponible', estilo="texto", font=FUENTES['normal_negrita']).grid(row=2, column=1, sticky="w", padx=5, pady=5)

    combo_horario = crear_combobox(campos, state='readonly')

    combo_horario.grid(
        row=3,
        column=1,
        sticky="ew",
        padx=5,
        pady=(0, 12)
    )

    # Funciones del formulario

    def obtener_fecha():
        try:
            fecha = datetime.strptime(
                entrada_fecha.get().strip(),
                "%Y-%m-%d"
            ).date()
            return fecha
        except ValueError:
            raise ValueError(
                "La fecha debe tener el formato AAAA-MM-DD."
            )

    def abrir_calendario():
        try:
            fecha_actual = obtener_fecha()
        except ValueError:
            fecha_actual = date.today()

        ventana_calendario = tk.Toplevel(nueva)
        ventana_calendario.title("Seleccionar fecha")
        ventana_calendario.resizable(False, False)
        ventana_calendario.transient(nueva)
        ventana_calendario.grab_set()

        mes_actual = [fecha_actual.year, fecha_actual.month]
        nombres_meses = (
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre",
            "Diciembre"
        )

        encabezado_calendario = ttk.Frame(ventana_calendario, padding=10)
        encabezado_calendario.pack(fill="x")

        encabezado_calendario.grid_columnconfigure(1, weight=1)
        titulo_mes = ttk.Label(
            encabezado_calendario,
            anchor="center",
            font=FUENTES["mediana_negrita"]
        )

        cuadrilla = ttk.Frame(ventana_calendario, padding=(10, 0, 10, 10))
        cuadrilla.pack()

        def seleccionar_dia(dia):
            fecha_seleccionada = date(mes_actual[0], mes_actual[1], dia)
            entrada_fecha.delete(0, tk.END)
            entrada_fecha.insert(0, fecha_seleccionada.isoformat())
            ventana_calendario.destroy()
            fecha_modificada()

        def dibujar_calendario():
            anio, mes = mes_actual
            titulo_mes.configure(text=f"{nombres_meses[mes - 1]} {anio}")

            for widget in cuadrilla.winfo_children():
                widget.destroy()

            for columna, dia_semana in enumerate(
                ("Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do")
            ):
                ttk.Label(
                    cuadrilla,
                    text=dia_semana,
                    anchor="center",
                    width=4
                ).grid(row=0, column=columna, padx=1, pady=2)

            for fila, semana in enumerate(
                calendar.monthcalendar(anio, mes),
                start=1
            ):
                for columna, dia in enumerate(semana):
                    if dia:
                        ttk.Button(
                            cuadrilla,
                            text=str(dia),
                            width=3,
                            command=lambda dia=dia: seleccionar_dia(dia)
                        ).grid(row=fila, column=columna, padx=1, pady=1)

        def cambiar_mes(cambio):
            anio, mes = mes_actual
            mes += cambio
            if mes < 1:
                mes_actual[:] = [anio - 1, 12]
            elif mes > 12:
                mes_actual[:] = [anio + 1, 1]
            else:
                mes_actual[:] = [anio, mes]
            dibujar_calendario()

        ttk.Button(
            encabezado_calendario,
            text="<",
            width=3,
            command=lambda: cambiar_mes(-1)
        ).grid(row=0, column=0)
        titulo_mes.grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(
            encabezado_calendario,
            text=">",
            width=3,
            command=lambda: cambiar_mes(1)
        ).grid(row=0, column=2)

        dibujar_calendario()

    crear_boton(marco_fecha, text='Calendario', command=abrir_calendario, estilo="secundario", font=('Arial', 9)).grid(row=0, column=1, padx=(6, 0), ipady=3)

    def actualizar_horarios(mostrar_mensaje=True):
        combo_horario.set("")
        combo_horario["values"] = []

        id_medico = obtener_id_seleccionado(combo_medico, medicos)
        if id_medico is None:
            if mostrar_mensaje:
                messagebox.showwarning(
                    "Aviso",
                    "Primero debes seleccionar un médico."
                )
            return

        try:
            fecha = obtener_fecha()

            disponibles = obtener_horarios_disponibles(
                conexion,
                id_medico,
                fecha,
                cita_edicion["id"]
            )

            combo_horario["values"] = disponibles

            if disponibles:
                combo_horario.current(0)

                if mostrar_mensaje:
                    horarios_texto = "\n".join(
                        f"• {horario}" for horario in disponibles
                    )

                    messagebox.showinfo(
                        "Horarios disponibles",
                        f"Se encontraron {len(disponibles)} horarios disponibles "
                        f"para el médico seleccionado:\n\n{horarios_texto}"
                    )
            else:
                if mostrar_mensaje:
                    messagebox.showinfo(
                        "Sin disponibilidad",
                        "No hay horarios disponibles para el médico "
                        "en la fecha seleccionada."
                    )

        except Exception as error:
            if mostrar_mensaje:
                messagebox.showerror(
                    "Error",
                    f"No fue posible consultar los horarios:\n{error}"
                )

    def fecha_modificada(event=None):
        if combo_medico.get() != "":
            actualizar_horarios(False)

    entrada_fecha.bind(
        "<FocusOut>",
        fecha_modificada
    )

    combo_medico.bind(
        "<<ComboboxSelected>>",
        lambda event: actualizar_horarios(False)
    )

    boton_horarios = crear_boton(campos, text='Consultar horarios', command=actualizar_horarios, estilo="secundario", font=('Arial', 9, 'bold'))

    boton_horarios.grid(
        row=4,
        column=1,
        sticky="e",
        padx=5,
        pady=3
    )

    def limpiar_formulario():

        cita_edicion["id"] = None

        combo_paciente.configure(state="readonly")
        combo_medico.configure(state="readonly")

        combo_paciente.set("")
        combo_medico.set("")
        combo_horario.set("")

        combo_horario["values"] = []

        entrada_fecha.delete(0, tk.END)
        entrada_fecha.insert(0, date.today().isoformat())

        boton_guardar.configure(
            text="Generar cita",
            bg=COLORES["azul"]
        )

    def guardar_cita():

        try:

            fecha = obtener_fecha()

            hora = combo_horario.get()
            es_actualizacion = cita_edicion["id"] is not None

            if not hora:
                messagebox.showwarning(
                    "Horario requerido",
                    "Selecciona un horario disponible.",
                    parent=nueva
                )
                return

            hora = datetime.strptime(hora, "%I:%M %p").time()

            if cita_edicion["id"] is not None:

                id_medico = obtener_id_seleccionado(combo_medico, medicos)
                if id_medico is None:
                    messagebox.showwarning(
                        "Médico requerido",
                        "Selecciona un médico.",
                        parent=nueva
                    )
                    return

                actualizar_cita(
                    conexion,
                    cita_edicion["id"],
                    id_medico,
                    fecha,
                    hora
                )

                messagebox.showinfo(
                    "Cita actualizada",
                    "La fecha y hora de la cita se actualizaron correctamente.",
                    parent=nueva
                )

            else:

                id_paciente = obtener_id_seleccionado(combo_paciente, pacientes)
                if id_paciente is None:
                    messagebox.showwarning(
                        "Paciente requerido",
                        "Selecciona un paciente.",
                        parent=nueva
                    )
                    return

                id_medico = obtener_id_seleccionado(combo_medico, medicos)
                if id_medico is None:
                    messagebox.showwarning(
                        "Médico requerido",
                        "Selecciona un médico.",
                        parent=nueva
                    )
                    return

                registrar_cita(
                    conexion,
                    id_paciente,
                    id_medico,
                    fecha,
                    hora
                )

                messagebox.showinfo(
                    "Cita registrada",
                    "La cita se registró correctamente.",
                    parent=nueva
                )

            if es_actualizacion:
                nueva.destroy()
            else:
                limpiar_formulario()

            if al_guardar is not None:
                al_guardar()

        except CitaDuplicadaError as error:
            messagebox.showerror(
                "Horario no disponible",
                str(error),
                parent=nueva
            )

        except Exception as error:

            messagebox.showerror(
                "Error al guardar",
                "No se pudo guardar la cita.\n\n" + str(error),
                parent=nueva
            )

    botones_formulario = crear_marco(formulario, estilo="superficie")

    botones_formulario.pack(
        fill="x",
        padx=20,
        pady=(0, 15)
    )

    boton_guardar = crear_boton(botones_formulario, text='Generar cita', command=guardar_cita, estilo="principal", width=18, activebackground=COLORES["azul_presionado"], activeforeground=COLORES["blanco"])

    boton_guardar.pack(side="right", padx=5, ipady=5)

    boton_limpiar = crear_boton(botones_formulario, text='Limpiar', command=limpiar_formulario, estilo="neutro", width=15)
    boton_limpiar.pack(side="right", padx=5, ipady=5)

    def cargar_cita_en_formulario(identificador):
        try:
            id_seleccionado = int(identificador)
            cita = obtener_cita(conexion, id_seleccionado)
        except (TypeError, ValueError) as error:
            messagebox.showerror(
                "Cita inválida",
                "No se pudo identificar la cita seleccionada.\n\n" + str(error),
                parent=nueva
            )
            return
        except Exception as error:
            messagebox.showerror(
                "Error",
                "No se pudo cargar la cita seleccionada.\n\n" + str(error),
                parent=nueva
            )
            return

        if cita is None:
            messagebox.showwarning(
                "Cita no encontrada",
                "La cita seleccionada ya no está disponible.",
                parent=nueva
            )
            return

        id_paciente, id_medico, fecha, hora = cita
        indice_paciente = next(
            (i for i, paciente in enumerate(pacientes)
             if paciente[0] == id_paciente),
            None
        )
        indice_medico = next(
            (i for i, medico in enumerate(medicos)
             if medico[0] == id_medico),
            None
        )

        if indice_paciente is None or indice_medico is None:
            messagebox.showerror(
                "Datos incompletos",
                "No se encontraron el paciente o el médico asociados a la cita.",
                parent=nueva
            )
            return

        cita_edicion["id"] = id_seleccionado
        combo_paciente.current(indice_paciente)
        combo_medico.current(indice_medico)
        combo_paciente.configure(state="disabled")
        combo_medico.configure(state="readonly")

        entrada_fecha.delete(0, tk.END)
        entrada_fecha.insert(0, fecha.strftime("%Y-%m-%d"))

        actualizar_horarios(False)
        combo_horario.set(hora.strftime("%I:%M %p"))
        boton_guardar.configure(text="Actualizar cita")
        boton_limpiar.configure(text="Cancelar", command=nueva.destroy)
        titulo_encabezado.configure(text="ACTUALIZAR CITA")

    try:

        lista_pacientes = obtener_pacientes(conexion)
        lista_medicos = obtener_medicos(conexion)

        pacientes.extend(lista_pacientes)
        medicos.extend(lista_medicos)

        combo_paciente["values"] = [paciente[1] for paciente in pacientes]
        combo_medico["values"] = [medico[1] for medico in medicos]

        if not pacientes:
            messagebox.showwarning(
                "Sin pacientes",
                "No hay pacientes registrados.",
                parent=nueva
            )

        if not medicos:
            messagebox.showwarning(
                "Sin médicos",
                "No hay médicos registrados.",
                parent=nueva
            )

        if id_cita is not None:
            cargar_cita_en_formulario(id_cita)

    except Exception as error:

        messagebox.showerror(
            "Error",
            "No se pudieron cargar los pacientes y médicos.\n\n"
            + str(error),
            parent=nueva
        )


def _cargar_citas_en_tabla(tabla, conexion, parent, contador=None, id_doctor=None):
    tabla.delete(*tabla.get_children())
    try:
        citas = obtener_citas(conexion, id_doctor=id_doctor)
        for cita in citas:
            tabla.insert(
                "",
                tk.END,
                values=(
                    cita[0],
                    cita[1],
                    cita[2],
                    cita[3].strftime("%Y-%m-%d"),
                    cita[4].strftime("%I:%M %p")
                )
            )
        if contador is not None:
            contador.configure(text=f"Registros encontrados: {len(citas)}")
        return len(citas)
    except Exception as error:
        messagebox.showerror(
            "Error",
            "No se pudieron cargar las citas.\n\n" + str(error),
            parent=parent
        )
        if contador is not None:
            contador.configure(text="Registros encontrados: 0")
        return 0


def abrir_consulta_citas(
    ventana,
    conexion,
    permitir_actualizacion=False,
    id_doctor=None
):
    consulta = tk.Toplevel(ventana)
    consulta.title("Citas registradas")
    consulta.geometry("850x500")
    consulta.minsize(650, 350)
    consulta.configure(bg=COLORES["fondo"])
    consulta.transient(ventana)

    crear_etiqueta(consulta, text='CITAS REGISTRADAS', estilo="encabezado", font=FUENTES['titulo_16'], pady=18).pack(fill="x")

    marco = crear_marco(consulta, estilo="superficie")
    marco.pack(fill="both", expand=True, padx=15, pady=15)

    columnas = ("id", "paciente", "medico", "fecha", "hora")
    tabla = crear_tabla_con_scroll(
        marco, columnas=columnas, horizontal=False, distribucion="pack"
    )

    for columna, etiqueta, ancho in (
        ("id", "ID", 60),
        ("paciente", "Paciente", 220),
        ("medico", "Médico", 220),
        ("fecha", "Fecha", 140),
        ("hora", "Hora", 100)
    ):
        tabla.heading(columna, text=etiqueta)
        tabla.column(
            columna,
            width=ancho,
            anchor="center" if columna in ("id", "fecha", "hora") else "w"
        )

    def cargar_citas():
        if permitir_actualizacion:
            boton_actualizar.configure(state="disabled")
        _cargar_citas_en_tabla(tabla, conexion, consulta, id_doctor=id_doctor)

    botones = crear_marco(consulta, estilo="fondo")
    botones.pack(pady=(0, 12))

    crear_boton(botones, text='Actualizar lista', command=cargar_citas, estilo="principal").pack(side="left", padx=5)

    if permitir_actualizacion:
        boton_actualizar = crear_boton(botones, text='Actualizar cita seleccionada', command=lambda: actualizar_cita_seleccionada(), estilo="accion", state='disabled')
        boton_actualizar.pack(side="left", padx=5)

        def cambiar_seleccion(event=None):
            boton_actualizar.configure(
                state="normal" if tabla.selection() else "disabled"
            )

        def actualizar_cita_seleccionada():
            seleccion = tabla.selection()
            if not seleccion:
                messagebox.showwarning(
                    "Cita requerida",
                    "Selecciona la cita que quieres actualizar.",
                    parent=consulta
                )
                return

            valores = tabla.item(seleccion[0], "values")
            try:
                id_seleccionado = int(valores[0])
            except (TypeError, ValueError, IndexError) as error:
                messagebox.showerror(
                    "Cita inválida",
                    "No se pudo identificar la cita seleccionada.\n\n" + str(error),
                    parent=consulta
                )
                return

            abrir_formulario_cita(
                consulta,
                conexion,
                cargar_citas,
                id_cita=id_seleccionado
            )

        tabla.bind("<<TreeviewSelect>>", cambiar_seleccion)

    cargar_citas()


def mostrar_consulta_citas(
    contenedor,
    conexion,
    contador=None,
    id_doctor=None,
    al_ver_paciente=None,
    boton_ver_paciente=None
):
    for widget in contenedor.winfo_children():
        widget.destroy()

    tabla_contenedor = crear_marco(contenedor, estilo="superficie")
    tabla_contenedor.pack(fill="both", expand=True)

    columnas = ("id", "paciente", "medico", "fecha", "hora")
    tabla = crear_tabla_con_scroll(
        tabla_contenedor, columnas=columnas
    )

    for columna, etiqueta, ancho in (
        ("id", "ID", 60),
        ("paciente", "Paciente", 200),
        ("medico", "Médico", 200),
        ("fecha", "Fecha", 120),
        ("hora", "Hora", 90)
    ):
        tabla.heading(columna, text=etiqueta)
        tabla.column(
            columna,
            width=ancho,
            anchor="center" if columna in ("id", "fecha", "hora") else "w"
        )

    _cargar_citas_en_tabla(
        tabla,
        conexion,
        contenedor.winfo_toplevel(),
        contador,
        id_doctor=id_doctor
    )

    if al_ver_paciente is not None:
        if boton_ver_paciente is not None:
            boton_ver_paciente.configure(state="disabled")

        def cambiar_seleccion(event=None):
            if boton_ver_paciente is not None:
                boton_ver_paciente.configure(
                    state="normal" if tabla.selection() else "disabled"
                )

        def ver_paciente_seleccionado():
            seleccion = tabla.selection()
            if not seleccion:
                return
            valores = tabla.item(seleccion[0], "values")
            try:
                id_cita = int(valores[0])
                cita = obtener_cita(conexion, id_cita)
                if not cita:
                    raise ValueError("La cita seleccionada ya no está disponible.")
                al_ver_paciente(cita[0])
            except Exception as error:
                messagebox.showerror(
                    "No se pudo abrir el paciente",
                    "No fue posible identificar al paciente de esta cita.\n\n"
                    + str(error),
                    parent=contenedor.winfo_toplevel()
                )

        if boton_ver_paciente is not None:
            boton_ver_paciente.configure(command=ver_paciente_seleccionado)
        tabla.bind("<<TreeviewSelect>>", cambiar_seleccion)



def mostrar_pagina_citas(
    panel, ventana, conexion, es_doctor, es_empleado,
    es_administrador, id_doctor_logueado, al_ver_paciente=None
):
    subtitulo_citas = (
        "Consulta tus citas m\u00e9dicas agendadas."
        if es_doctor
        else "Genera, consulta y actualiza citas m\u00e9dicas."
    )
    _, contador_citas = crear_encabezado_seccion(
        panel,
        "Citas",
        subtitulo_citas,
        mostrar_contador=True
    )

    botones_citas = crear_marco(panel, estilo="superficie")
    botones_citas.pack(fill="x", padx=20, pady=15)

    boton_ver_paciente = None

    area_resultados_citas = crear_marco(panel, estilo="superficie")
    area_resultados_citas.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    filtro_doctor = (
        id_doctor_logueado if id_doctor_logueado is not None else -1
    ) if es_doctor else None

    crear_boton(
        botones_citas,
        text='Consultar citas',
        command=lambda: mostrar_consulta_citas(
            area_resultados_citas,
            conexion,
            contador_citas,
            id_doctor=filtro_doctor,
            al_ver_paciente=al_ver_paciente,
            boton_ver_paciente=boton_ver_paciente
        ),
        estilo="accion",
        width=16
    ).pack(side="left", padx=3)

    if al_ver_paciente is not None:
        boton_ver_paciente = crear_boton(
            botones_citas,
            text='Ver información',
            command=lambda: None,
            estilo="principal",
            width=17,
            state="disabled"
        )
        boton_ver_paciente.pack(side="left", padx=3)

    # Solo Empleado o Administrador pueden generar o modificar citas
    if es_empleado or es_administrador:
        crear_boton(botones_citas, text='Actualizar cita', command=lambda: abrir_consulta_citas(ventana, conexion, permitir_actualizacion=True), estilo="principal", width=17).pack(side="left", padx=3)

        crear_boton(botones_citas, text='Generar cita', command=lambda: abrir_formulario_cita(ventana, conexion), estilo="principal", width=14).pack(side="left", padx=3)
