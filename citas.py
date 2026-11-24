import calendar
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

from consultas_citas import (
    CitaDuplicadaError,
    obtener_pacientes,
    obtener_medicos,
    obtener_horarios_disponibles,
    registrar_cita,
    obtener_citas,
    obtener_cita,
    actualizar_cita
)


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
    nueva.configure(bg="#F0F2F5")

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

    encabezado = tk.Frame(
        nueva,
        bg="#1F4E79",
        height=75
    )

    encabezado.pack(fill="x")
    encabezado.pack_propagate(False)

    titulo_encabezado = tk.Label(
        encabezado,
        text="ACTUALIZAR CITA" if id_cita is not None else "GENERAR CITA",
        font=("Arial", 19, "bold"),
        bg="#1F4E79",
        fg="white"
    )
    titulo_encabezado.pack(anchor="w", padx=25, pady=(15, 2))

    tk.Label(
        encabezado,
        text=(
            "Modifica el médico, la fecha o el horario."
            if id_cita is not None
            else "Programa una cita médica."
        ),
        font=("Arial", 10),
        bg="#1F4E79",
        fg="#DCE8F5"
    ).pack(anchor="w", padx=25)

    def regresar_menu():
        nueva.destroy()

    tk.Button(
        encabezado,
        text="Regresar al menú",
        command=regresar_menu,
        bg="#E8EEF5",
        fg="#1F4E79",
        activebackground="#D0DFEF",
        relief="flat",
        font=("Arial", 9, "bold"),
        cursor="hand2"
    ).place(
        relx=0.98,
        rely=0.5,
        anchor="e"
    )

    # Contenedor principal

    principal = tk.Frame(
        nueva,
        bg="#F0F2F5"
    )

    principal.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=15
    )

    # Formulario

    formulario = tk.Frame(
        principal,
        bg="white",
        relief="solid",
        borderwidth=1
    )

    formulario.pack(
        fill="x",
        pady=(0, 12)
    )

    tk.Label(
        formulario,
        text="Datos de la cita",
        font=("Arial", 14, "bold"),
        bg="white",
        fg="#1F4E79"
    ).pack(anchor="w", padx=20, pady=(15, 10))

    campos = tk.Frame(
        formulario,
        bg="white"
    )

    campos.pack(
        fill="x",
        padx=20,
        pady=(0, 15)
    )

    campos.grid_columnconfigure(0, weight=1)
    campos.grid_columnconfigure(1, weight=1)

    # Pacientes

    tk.Label(
        campos,
        text="Paciente",
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#333333"
    ).grid(row=0, column=0, sticky="w", padx=5, pady=5)

    combo_paciente = ttk.Combobox(
        campos,
        state="readonly",
        font=("Arial", 10)
    )

    combo_paciente.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=5,
        pady=(0, 12)
    )

    # Doctores

    tk.Label(
        campos,
        text="Médico",
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#333333"
    ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

    combo_medico = ttk.Combobox(
        campos,
        state="readonly",
        font=("Arial", 10)
    )

    combo_medico.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=5,
        pady=(0, 12)
    )

    # Fecha

    tk.Label(
        campos,
        text="Fecha (AAAA-MM-DD)",
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#333333"
    ).grid(row=2, column=0, sticky="w", padx=5, pady=5)

    marco_fecha = tk.Frame(campos, bg="white")
    marco_fecha.grid(
        row=3,
        column=0,
        sticky="ew",
        padx=5,
        pady=(0, 12)
    )
    marco_fecha.grid_columnconfigure(0, weight=1)

    entrada_fecha = tk.Entry(
        marco_fecha,
        font=("Arial", 10),
        relief="solid",
        borderwidth=1
    )
    entrada_fecha.grid(row=0, column=0, sticky="ew", ipady=6)

    entrada_fecha.insert(0, date.today().isoformat())

    # Horario

    tk.Label(
        campos,
        text="Horario disponible",
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#333333"
    ).grid(row=2, column=1, sticky="w", padx=5, pady=5)

    combo_horario = ttk.Combobox(
        campos,
        state="readonly",
        font=("Arial", 10)
    )

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
            font=("Arial", 11, "bold")
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

    tk.Button(
        marco_fecha,
        text="Calendario",
        command=abrir_calendario,
        bg="#E8EEF5",
        fg="#1F4E79",
        relief="flat",
        font=("Arial", 9),
        cursor="hand2"
    ).grid(row=0, column=1, padx=(6, 0), ipady=3)

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

    boton_horarios = tk.Button(
        campos,
        text="Consultar horarios",
        command=actualizar_horarios,
        bg="#E8EEF5",
        fg="#1F4E79",
        relief="flat",
        font=("Arial", 9, "bold"),
        cursor="hand2"
    )

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
            bg="#1F4E79"
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

    botones_formulario = tk.Frame(
        formulario,
        bg="white"
    )

    botones_formulario.pack(
        fill="x",
        padx=20,
        pady=(0, 15)
    )

    boton_guardar = tk.Button(
        botones_formulario,
        text="Generar cita",
        command=guardar_cita,
        width=18,
        bg="#1F4E79",
        fg="white",
        activebackground="#163A5A",
        activeforeground="white",
        relief="flat",
        font=("Arial", 10, "bold"),
        cursor="hand2"
    )

    boton_guardar.pack(side="right", padx=5, ipady=5)

    boton_limpiar = tk.Button(
        botones_formulario,
        text="Limpiar",
        command=limpiar_formulario,
        width=15,
        bg="#E0E4E8",
        fg="#333333",
        relief="flat",
        font=("Arial", 10),
        cursor="hand2"
    )
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
    consulta.configure(bg="#F0F2F5")
    consulta.transient(ventana)

    tk.Label(
        consulta,
        text="CITAS REGISTRADAS",
        font=("Arial", 16, "bold"),
        bg="#1F4E79",
        fg="white",
        pady=18
    ).pack(fill="x")

    marco = tk.Frame(consulta, bg="white")
    marco.pack(fill="both", expand=True, padx=15, pady=15)

    columnas = ("id", "paciente", "medico", "fecha", "hora")
    tabla = ttk.Treeview(marco, columns=columnas, show="headings")

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

    scroll = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll.set)
    tabla.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    def cargar_citas():
        if permitir_actualizacion:
            boton_actualizar.configure(state="disabled")
        _cargar_citas_en_tabla(tabla, conexion, consulta, id_doctor=id_doctor)

    botones = tk.Frame(consulta, bg="#F0F2F5")
    botones.pack(pady=(0, 12))

    tk.Button(
        botones,
        text="Actualizar lista",
        command=cargar_citas,
        bg="#1F4E79",
        fg="white",
        relief="flat",
        font=("Arial", 10, "bold"),
        cursor="hand2"
    ).pack(side="left", padx=5)

    if permitir_actualizacion:
        boton_actualizar = tk.Button(
            botones,
            text="Actualizar cita seleccionada",
            command=lambda: actualizar_cita_seleccionada(),
            state="disabled",
            bg="#5A8FC4",
            fg="white",
            relief="flat",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
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
    id_doctor=None
):
    for widget in contenedor.winfo_children():
        widget.destroy()

    tabla_contenedor = tk.Frame(contenedor, bg="white")
    tabla_contenedor.pack(fill="both", expand=True)

    columnas = ("id", "paciente", "medico", "fecha", "hora")
    tabla = ttk.Treeview(
        tabla_contenedor,
        columns=columnas,
        show="headings"
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

    scroll_vertical = ttk.Scrollbar(
        tabla_contenedor,
        orient="vertical",
        command=tabla.yview
    )
    scroll_horizontal = ttk.Scrollbar(
        tabla_contenedor,
        orient="horizontal",
        command=tabla.xview
    )
    tabla.configure(
        yscrollcommand=scroll_vertical.set,
        xscrollcommand=scroll_horizontal.set
    )
    tabla.grid(row=0, column=0, sticky="nsew")
    scroll_vertical.grid(row=0, column=1, sticky="ns")
    scroll_horizontal.grid(row=1, column=0, sticky="ew")
    tabla_contenedor.grid_rowconfigure(0, weight=1)
    tabla_contenedor.grid_columnconfigure(0, weight=1)

    _cargar_citas_en_tabla(
        tabla,
        conexion,
        contenedor.winfo_toplevel(),
        contador,
        id_doctor=id_doctor
    )
