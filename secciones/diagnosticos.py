import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from operaciones_sql.consultas_medicas import (
    guardar_consulta_medica,
    obtener_historial_paciente,
    obtener_medicamentos_catalogo,
    obtener_pacientes_doctor
)
from utilidades.recetas import generar_pdf_receta
from utilidades.diseno import COLORES, FUENTES, crear_boton, crear_etiqueta


def abrir_ventana_consulta_medica(
    ventana,
    conexion,
    id_doctor,
    nombre_doctor,
    al_guardar=None
):
    pacientes_cols, pacientes_filas = obtener_pacientes_doctor(conexion, id_doctor)
    if not pacientes_filas:
        messagebox.showwarning(
            "Sin pacientes asignados",
            "No tienes pacientes con citas registradas para realizar una consulta.",
            parent=ventana
        )
        return

    idx_id = pacientes_cols.index("id_paciente") if "id_paciente" in pacientes_cols else 0
    idx_nombre = pacientes_cols.index("nombre") if "nombre" in pacientes_cols else 1
    lista_pacientes = [(fila[idx_id], fila[idx_nombre]) for fila in pacientes_filas]
    catalogo_medicamentos = obtener_medicamentos_catalogo(conexion)

    modal = tk.Toplevel(ventana)
    modal.title("Consulta Médica y Receta")
    modal.geometry("880x660")
    modal.minsize(780, 600)
    modal.configure(bg=COLORES["fondo"])
    modal.transient(ventana)
    modal.grab_set()

    # Encabezado
    encabezado = tk.Frame(modal, bg=COLORES["azul"], height=75)
    encabezado.pack(fill="x")
    encabezado.pack_propagate(False)

    crear_etiqueta(encabezado, text='CONSULTA MÉDICA E HISTORIAL CLÍNICO', estilo="encabezado", font=FUENTES['titulo_17']).pack(anchor="w", padx=20, pady=(14, 2))

    crear_etiqueta(encabezado, text=f'Médico tratante: {nombre_doctor}', estilo="sobre_azul", font=FUENTES['normal']).pack(anchor="w", padx=20)

    cuerpo = tk.Frame(modal, bg=COLORES["fondo"])
    cuerpo.pack(fill="both", expand=True, padx=15, pady=12)

    # Selección de paciente
    marco_paciente = tk.Frame(cuerpo, bg=COLORES["blanco"], relief="solid", borderwidth=1)
    marco_paciente.pack(fill="x", pady=(0, 10))

    fila_pac = tk.Frame(marco_paciente, bg=COLORES["blanco"])
    fila_pac.pack(fill="x", padx=15, pady=10)

    crear_etiqueta(fila_pac, text='Paciente con cita:', estilo="texto", font=FUENTES['normal_negrita']).pack(side="left", padx=(0, 10))

    combo_paciente = ttk.Combobox(
        fila_pac,
        state="readonly",
        font=FUENTES["normal"],
        width=40,
        values=[p[1] for p in lista_pacientes]
    )
    combo_paciente.pack(side="left", fill="x", expand=True)

    # Cuadro de texto de Diagnóstico (Historial del paciente)
    marco_diag = tk.Frame(cuerpo, bg=COLORES["blanco"], relief="solid", borderwidth=1)
    marco_diag.pack(fill="both", expand=True, pady=(0, 10))

    crear_etiqueta(marco_diag, text='Diagnóstico e Historial Clínico del Paciente', estilo="titulo", font=FUENTES['mediana_negrita']).pack(anchor="w", padx=15, pady=(10, 5))

    contenedor_texto = tk.Frame(marco_diag, bg=COLORES["blanco"])
    contenedor_texto.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    texto_diagnostico = tk.Text(
        contenedor_texto,
        font=FUENTES["normal"],
        height=10,
        wrap="word",
        relief="solid",
        borderwidth=1
    )
    scroll_texto = ttk.Scrollbar(
        contenedor_texto,
        orient="vertical",
        command=texto_diagnostico.yview
    )
    texto_diagnostico.configure(yscrollcommand=scroll_texto.set)
    texto_diagnostico.pack(side="left", fill="both", expand=True)
    scroll_texto.pack(side="right", fill="y")

    # Sección de Medicamento y Tratamiento
    marco_med = tk.Frame(cuerpo, bg=COLORES["blanco"], relief="solid", borderwidth=1)
    marco_med.pack(fill="x", pady=(0, 10))

    crear_etiqueta(marco_med, text='Prescripción de Medicamento', estilo="titulo", font=FUENTES['mediana_negrita']).pack(anchor="w", padx=15, pady=(10, 5))

    grid_med = tk.Frame(marco_med, bg=COLORES["blanco"])
    grid_med.pack(fill="x", padx=15, pady=(0, 10))
    grid_med.grid_columnconfigure(0, weight=2)
    grid_med.grid_columnconfigure(1, weight=1)
    grid_med.grid_columnconfigure(2, weight=1)

    crear_etiqueta(grid_med, text='Medicamento', estilo="texto", font=FUENTES['compacta_negrita']).grid(row=0, column=0, sticky="w", padx=4)

    crear_etiqueta(grid_med, text='Días de tratamiento', estilo="texto", font=FUENTES['compacta_negrita']).grid(row=0, column=1, sticky="w", padx=4)

    crear_etiqueta(grid_med, text='Horario de suministro', estilo="texto", font=FUENTES['compacta_negrita']).grid(row=0, column=2, sticky="w", padx=4)

    combo_medicamento = ttk.Combobox(
        grid_med,
        state="readonly" if catalogo_medicamentos else "normal",
        font=FUENTES["normal"],
        values=[m[1] for m in catalogo_medicamentos]
    )
    combo_medicamento.grid(row=1, column=0, sticky="ew", padx=4, pady=4, ipady=3)
    if catalogo_medicamentos:
        combo_medicamento.current(0)

    entrada_dias = tk.Entry(
        grid_med,
        font=FUENTES["normal"],
        relief="solid",
        borderwidth=1
    )
    entrada_dias.grid(row=1, column=1, sticky="ew", padx=4, pady=4, ipady=4)
    entrada_dias.insert(0, "7 días")

    entrada_horario = tk.Entry(
        grid_med,
        font=FUENTES["normal"],
        relief="solid",
        borderwidth=1
    )
    entrada_horario.grid(row=1, column=2, sticky="ew", padx=4, pady=4, ipady=4)
    entrada_horario.insert(0, "Cada 8 horas")

    def cargar_historial_seleccionado(event=None):
        indice = combo_paciente.current()
        if indice < 0:
            return
        id_pac = lista_pacientes[indice][0]
        historial = obtener_historial_paciente(conexion, id_pac)
        texto_diagnostico.delete("1.0", tk.END)
        fecha_hoy = date.today().isoformat()
        plantilla = f"Consulta ({fecha_hoy}) - Dr(a). {nombre_doctor}:\nDiagnóstico: "
        if historial:
            texto_diagnostico.insert(
                "1.0",
                f"=== HISTORIAL PREVIO ==={historial}\n\n=== CONSULTA ACTUAL ===\n{plantilla}"
            )
        else:
            texto_diagnostico.insert("1.0", plantilla)

    combo_paciente.bind("<<ComboboxSelected>>", cargar_historial_seleccionado)
    combo_paciente.current(0)
    cargar_historial_seleccionado()

    def obtener_datos_medicamento():
        indice_med = combo_medicamento.current()
        if catalogo_medicamentos and 0 <= indice_med < len(catalogo_medicamentos):
            id_med = catalogo_medicamentos[indice_med][0]
            nombre_med = catalogo_medicamentos[indice_med][1]
        else:
            id_med = None
            nombre_med = combo_medicamento.get().strip()

        dias = entrada_dias.get().strip()
        horario = entrada_horario.get().strip()
        return id_med, nombre_med, dias, horario

    def agregar_tratamiento_al_diagnostico():
        _, nombre_med, dias, horario = obtener_datos_medicamento()
        if not nombre_med:
            messagebox.showwarning(
                "Medicamento requerido",
                "Selecciona o escribe un medicamento.",
                parent=modal
            )
            return
        if not dias or not horario:
            messagebox.showwarning(
                "Datos incompletos",
                "Indica los días de tratamiento y el horario de suministro.",
                parent=modal
            )
            return

        bloque_receta = (
            f"\n[Tratamiento indicado] Medicamento: {nombre_med} | "
            f"Días: {dias} | Horario: {horario}\n"
        )
        texto_diagnostico.insert(tk.END, bloque_receta)

    crear_boton(grid_med, text='Agregar medicamento al diagnóstico', command=agregar_tratamiento_al_diagnostico, estilo="secundario", font=('Arial', 9, 'bold')).grid(row=2, column=0, columnspan=3, sticky="e", padx=4, pady=(4, 0))

    # Botones inferiores
    botones = tk.Frame(cuerpo, bg=COLORES["fondo"])
    botones.pack(fill="x", pady=(2, 0))

    def accion_generar_receta():
        indice_pac = combo_paciente.current()
        if indice_pac < 0:
            messagebox.showwarning(
                "Paciente requerido",
                "Selecciona un paciente.",
                parent=modal
            )
            return

        nombre_paciente = lista_pacientes[indice_pac][1]
        _, nombre_med, dias, horario = obtener_datos_medicamento()

        if not nombre_med or not dias or not horario:
            messagebox.showwarning(
                "Prescripción incompleta",
                "Completa el medicamento, los días de tratamiento y el horario de suministro.",
                parent=modal
            )
            return

        diagnostico_texto = texto_diagnostico.get("1.0", tk.END).strip()
        try:
            ruta_pdf = generar_pdf_receta(
                nombre_paciente=nombre_paciente,
                nombre_doctor=nombre_doctor,
                medicamento=nombre_med,
                dias_tratamiento=dias,
                horario_suministro=horario,
                indicaciones=diagnostico_texto,
                ruta_salida="receta.pdf"
            )
            messagebox.showinfo(
                "Receta generada",
                f"La receta se generó correctamente en:\n{ruta_pdf}",
                parent=modal
            )
        except Exception as error:
            messagebox.showerror(
                "Error al generar receta",
                str(error),
                parent=modal
            )

    def accion_guardar_consulta():
        indice_pac = combo_paciente.current()
        if indice_pac < 0:
            messagebox.showwarning(
                "Paciente requerido",
                "Selecciona un paciente.",
                parent=modal
            )
            return

        id_pac = lista_pacientes[indice_pac][0]
        id_med, nombre_med, dias, horario = obtener_datos_medicamento()
        contenido_diag = texto_diagnostico.get("1.0", tk.END).strip()

        if not contenido_diag:
            messagebox.showwarning(
                "Diagnóstico vacío",
                "Escribe el diagnóstico del paciente antes de guardar.",
                parent=modal
            )
            return

        if nombre_med and "[Tratamiento indicado]" not in contenido_diag:
            contenido_diag += (
                f"\n[Tratamiento indicado] Medicamento: {nombre_med} | "
                f"Días: {dias} | Horario: {horario}"
            )

        try:
            guardar_consulta_medica(
                conexion=conexion,
                id_paciente=id_pac,
                id_doctor=id_doctor,
                diagnostico_completo=contenido_diag,
                id_medicamento=id_med
            )
            messagebox.showinfo(
                "Consulta guardada",
                "El diagnóstico y tratamiento se registraron en el historial del paciente.",
                parent=modal
            )
            if al_guardar is not None:
                al_guardar()
        except Exception as error:
            messagebox.showerror(
                "Error al guardar consulta",
                str(error),
                parent=modal
            )

    crear_boton(botones, text='Cerrar', command=modal.destroy, estilo="neutro", width=14).pack(side="left", ipady=5)

    crear_boton(botones, text='Guardar consulta', command=accion_guardar_consulta, estilo="principal", width=18).pack(side="right", padx=(6, 0), ipady=5)

    crear_boton(botones, text='GENERAR RECETA', command=accion_generar_receta, estilo="exito", width=18, activebackground=COLORES["verde_presionado"], activeforeground=COLORES["blanco"]).pack(side="right", padx=6, ipady=5)
