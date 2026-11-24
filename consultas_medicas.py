import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from pathlib import Path
from psycopg2 import sql


def _tabla_existe(conexion, nombre_tabla):
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            );
        """, (nombre_tabla,))
        return bool(cursor.fetchone()[0])
    finally:
        cursor.close()


def _columnas_tabla(conexion, nombre_tabla):
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = %s
            ORDER BY ordinal_position;
        """, (nombre_tabla,))
        return [fila[0] for fila in cursor.fetchall()]
    finally:
        cursor.close()


def _detectar_tabla_consulta(conexion):
    for candidata in ("consulta", "consultas"):
        if _tabla_existe(conexion, candidata):
            return candidata
    return None


def _detectar_tabla_medicamento(conexion):
    for candidata in ("medicamento", "medicamentos"):
        if _tabla_existe(conexion, candidata):
            return candidata
    return None


def obtener_pacientes_doctor(conexion, id_doctor):
    cursor = conexion.cursor()
    try:
        columnas = _columnas_tabla(conexion, "paciente")
        if not columnas:
            return [], []

        select_cols = sql.SQL(", ").join(
            sql.SQL("p.{}").format(sql.Identifier(col))
            for col in columnas
        )
        consulta = sql.SQL("""
            SELECT DISTINCT {cols}
            FROM paciente p
            INNER JOIN cita c
                ON p.id_paciente = c.id_paciente
            WHERE c.id_doctor = %s
            ORDER BY p.id_paciente ASC;
        """).format(cols=select_cols)

        cursor.execute(consulta, (id_doctor,))
        return columnas, cursor.fetchall()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()


def obtener_medicamentos_catalogo(conexion):
    tabla_med = _detectar_tabla_medicamento(conexion)
    if not tabla_med:
        return []

    columnas = _columnas_tabla(conexion, tabla_med)
    cursor = conexion.cursor()
    try:
        if all(
            c in columnas
            for c in ("id_medicamento", "nombre", "presentacion", "via_de_administracion")
        ):
            cursor.execute("""
                SELECT
                    id_medicamento,
                    nombre,
                    presentacion,
                    via_de_administracion,
                    fecha_caducidad
                FROM medicamento
                ORDER BY id_medicamento ASC;
            """)
            resultados = []
            for id_med, nombre, presentacion, via, caducidad in cursor.fetchall():
                detalles = []
                if presentacion:
                    detalles.append(str(presentacion))
                if via:
                    detalles.append(f"Vía: {via}")
                etiqueta = (
                    f"{nombre} ({' - '.join(detalles)})"
                    if detalles else str(nombre)
                )
                resultados.append((id_med, etiqueta, str(nombre)))
            return resultados

        col_id = columnas[0]
        col_nombre = next(
            (c for c in columnas if "nombre" in c.lower()),
            columnas[1] if len(columnas) > 1 else columnas[0]
        )
        consulta = sql.SQL("SELECT {}, {} FROM {} ORDER BY {} ASC;").format(
            sql.Identifier(col_id),
            sql.Identifier(col_nombre),
            sql.Identifier(tabla_med),
            sql.Identifier(col_id)
        )
        cursor.execute(consulta)
        return [(f[0], str(f[1]), str(f[1])) for f in cursor.fetchall()]
    except Exception:
        conexion.rollback()
        return []
    finally:
        cursor.close()


def obtener_consultas_doctor(conexion, id_doctor=None):
    tabla_consulta = _detectar_tabla_consulta(conexion)
    if not tabla_consulta:
        return [], []

    columnas = _columnas_tabla(conexion, tabla_consulta)
    cursor = conexion.cursor()
    try:
        if (
            id_doctor is not None
            and "id_cita" in columnas
            and _detectar_tabla_medicamento(conexion)
        ):
            cursor.execute("""
                SELECT
                    con.id_consulta,
                    con.id_cita,
                    p.nombre AS paciente,
                    c.fecha AS fecha_cita,
                    con.diagnostico,
                    COALESCE(m.nombre, 'Sin medicamento') AS medicamento
                FROM consulta con
                INNER JOIN cita c
                    ON con.id_cita = c.id_cita
                INNER JOIN paciente p
                    ON c.id_paciente = p.id_paciente
                LEFT JOIN medicamento m
                    ON con.id_medicamento = m.id_medicamento
                WHERE c.id_doctor = %s
                ORDER BY con.id_consulta ASC;
            """, (id_doctor,))
            cols_vista = [
                "id_consulta",
                "id_cita",
                "paciente",
                "fecha_cita",
                "diagnostico",
                "medicamento"
            ]
            return cols_vista, cursor.fetchall()

        if id_doctor is not None and "id_cita" in columnas:
            consulta = sql.SQL("""
                SELECT con.*
                FROM {} con
                INNER JOIN cita c
                    ON con.id_cita = c.id_cita
                WHERE c.id_doctor = %s
                ORDER BY 1 ASC;
            """).format(sql.Identifier(tabla_consulta))
            cursor.execute(consulta, (id_doctor,))
        else:
            consulta = sql.SQL("""
                SELECT *
                FROM {}
                ORDER BY 1 ASC;
            """).format(sql.Identifier(tabla_consulta))
            cursor.execute(consulta)

        return columnas, cursor.fetchall()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()


def obtener_historial_paciente(conexion, id_paciente):
    tabla_consulta = _detectar_tabla_consulta(conexion)
    if not tabla_consulta:
        return ""

    columnas = _columnas_tabla(conexion, tabla_consulta)
    if "diagnostico" not in columnas:
        return ""

    cursor = conexion.cursor()
    try:
        if "id_cita" in columnas:
            cursor.execute("""
                SELECT c.fecha, con.diagnostico
                FROM consulta con
                INNER JOIN cita c
                    ON con.id_cita = c.id_cita
                WHERE c.id_paciente = %s
                ORDER BY con.id_consulta ASC;
            """, (id_paciente,))
        elif "id_paciente" in columnas:
            cursor.execute("""
                SELECT NULL, diagnostico
                FROM consulta
                WHERE id_paciente = %s
                ORDER BY 1 ASC;
            """, (id_paciente,))
        else:
            return ""

        filas = cursor.fetchall()
        bloques = []
        for fecha_reg, diag in filas:
            if diag:
                encabezado = f"[{fecha_reg}] " if fecha_reg else ""
                bloques.append(f"{encabezado}{diag.strip()}")
        return "\n" + ("-" * 45) + "\n".join([""] + bloques) if bloques else ""
    except Exception:
        conexion.rollback()
        return ""
    finally:
        cursor.close()


def guardar_consulta_medica(
    conexion,
    id_paciente,
    id_doctor,
    diagnostico_completo,
    id_medicamento=None
):
    tabla_consulta = _detectar_tabla_consulta(conexion)
    if not tabla_consulta:
        raise ValueError(
            "No se encontró la tabla 'consulta' en la base de datos."
        )

    columnas = _columnas_tabla(conexion, tabla_consulta)
    cursor = conexion.cursor()

    try:
        campos = []
        valores = []

        if "id_cita" in columnas:
            cursor.execute("""
                SELECT id_cita
                FROM cita
                WHERE id_paciente = %s
                AND id_doctor = %s
                ORDER BY fecha DESC, hora DESC, id_cita DESC
                LIMIT 1;
            """, (id_paciente, id_doctor))
            fila_cita = cursor.fetchone()
            if fila_cita is None:
                raise ValueError(
                    "El paciente seleccionado no tiene una cita registrada con este doctor."
                )
            campos.append("id_cita")
            valores.append(fila_cita[0])

        if "diagnostico" in columnas:
            campos.append("diagnostico")
            valores.append(diagnostico_completo)

        if "id_medicamento" in columnas and id_medicamento is not None:
            campos.append("id_medicamento")
            valores.append(id_medicamento)

        if not campos:
            raise ValueError(
                "No se pudieron mapear las columnas de la tabla consulta."
            )

        consulta = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(tabla_consulta),
            sql.SQL(", ").join(map(sql.Identifier, campos)),
            sql.SQL(", ").join(sql.Placeholder() for _ in valores)
        )
        cursor.execute(consulta, valores)
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()


def generar_pdf_receta(
    nombre_paciente,
    nombre_doctor,
    medicamento,
    dias_tratamiento,
    horario_suministro,
    indicaciones="",
    ruta_salida="receta.pdf"
):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
    except ImportError as exc:
        raise ImportError(
            "Para generar el archivo PDF instala 'reportlab' ejecutando:\n"
            "pip install reportlab"
        ) from exc

    c = canvas.Canvas(str(ruta_salida), pagesize=letter)
    ancho, alto = letter

    # Encabezado institucional
    c.setFillColor(colors.HexColor("#1F4E79"))
    c.rect(40, alto - 125, ancho - 80, 85, fill=1, stroke=0)

    ruta_logo = Path(__file__).resolve().parent / "imagenes" / "nd.png"
    texto_x = 60
    if ruta_logo.exists():
        c.drawImage(
            str(ruta_logo),
            52,
            alto - 117,
            width=68,
            height=68,
            preserveAspectRatio=True,
            mask="auto"
        )
        texto_x = 135

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(texto_x, alto - 75, "NÚCLEO DE DIAGNÓSTICO")
    c.setFont("Helvetica", 11)
    c.drawString(texto_x, alto - 96, "Receta Médica")

    c.setFont("Helvetica", 9)
    fecha_emision = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    c.drawRightString(ancho - 55, alto - 112, f"Fecha: {fecha_emision}")

    # Datos del Paciente
    y = alto - 165
    c.setFillColor(colors.HexColor("#1F4E79"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "DATOS DEL PACIENTE")
    c.line(50, y - 5, ancho - 50, y - 5)

    y -= 28
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Paciente:")
    c.setFont("Helvetica", 11)
    c.drawString(120, y, nombre_paciente)

    # Información del Medicamento
    y -= 45
    c.setFillColor(colors.HexColor("#1F4E79"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "PRESCRIPCIÓN Y MEDICAMENTO INDICADO")
    c.line(50, y - 5, ancho - 50, y - 5)

    y -= 30
    c.setFillColor(colors.HexColor("#F4F7FA"))
    c.rect(50, y - 75, ancho - 100, 90, fill=1, stroke=1)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(65, y - 5, "Medicamento:")
    c.setFont("Helvetica", 11)
    c.drawString(165, y - 5, medicamento)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(65, y - 30, "Días de tratamiento:")
    c.setFont("Helvetica", 11)
    c.drawString(200, y - 30, dias_tratamiento)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(65, y - 55, "Horario de suministro:")
    c.setFont("Helvetica", 11)
    c.drawString(215, y - 55, horario_suministro)

    # Indicaciones / Diagnóstico
    if indicaciones.strip():
        y -= 115
        c.setFillColor(colors.HexColor("#1F4E79"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "INDICACIONES / DIAGNÓSTICO")
        c.line(50, y - 5, ancho - 50, y - 5)

        y -= 25
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        for linea in indicaciones.strip().splitlines()[:14]:
            c.drawString(55, y, linea[:95])
            y -= 15

    # Firma del Doctor
    firma_y = 110
    c.setStrokeColor(colors.HexColor("#1F4E79"))
    c.line(ancho / 2 - 130, firma_y, ancho / 2 + 130, firma_y)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(ancho / 2, firma_y - 18, f"Dr(a). {nombre_doctor}")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawCentredString(ancho / 2, firma_y - 33, "Médico Tratante - Núcleo de Diagnóstico")

    c.save()
    return str(Path(ruta_salida).resolve())


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
    modal.configure(bg="#F0F2F5")
    modal.transient(ventana)
    modal.grab_set()

    # Encabezado
    encabezado = tk.Frame(modal, bg="#1F4E79", height=75)
    encabezado.pack(fill="x")
    encabezado.pack_propagate(False)

    tk.Label(
        encabezado,
        text="CONSULTA MÉDICA E HISTORIAL CLÍNICO",
        font=("Arial", 17, "bold"),
        bg="#1F4E79",
        fg="white"
    ).pack(anchor="w", padx=20, pady=(14, 2))

    tk.Label(
        encabezado,
        text=f"Médico tratante: {nombre_doctor}",
        font=("Arial", 10),
        bg="#1F4E79",
        fg="#DCE8F5"
    ).pack(anchor="w", padx=20)

    cuerpo = tk.Frame(modal, bg="#F0F2F5")
    cuerpo.pack(fill="both", expand=True, padx=15, pady=12)

    # Selección de paciente
    marco_paciente = tk.Frame(cuerpo, bg="white", relief="solid", borderwidth=1)
    marco_paciente.pack(fill="x", pady=(0, 10))

    fila_pac = tk.Frame(marco_paciente, bg="white")
    fila_pac.pack(fill="x", padx=15, pady=10)

    tk.Label(
        fila_pac,
        text="Paciente con cita:",
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#333333"
    ).pack(side="left", padx=(0, 10))

    combo_paciente = ttk.Combobox(
        fila_pac,
        state="readonly",
        font=("Arial", 10),
        width=40,
        values=[p[1] for p in lista_pacientes]
    )
    combo_paciente.pack(side="left", fill="x", expand=True)

    # Cuadro de texto de Diagnóstico (Historial del paciente)
    marco_diag = tk.Frame(cuerpo, bg="white", relief="solid", borderwidth=1)
    marco_diag.pack(fill="both", expand=True, pady=(0, 10))

    tk.Label(
        marco_diag,
        text="Diagnóstico e Historial Clínico del Paciente",
        font=("Arial", 11, "bold"),
        bg="white",
        fg="#1F4E79"
    ).pack(anchor="w", padx=15, pady=(10, 5))

    contenedor_texto = tk.Frame(marco_diag, bg="white")
    contenedor_texto.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    texto_diagnostico = tk.Text(
        contenedor_texto,
        font=("Arial", 10),
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
    marco_med = tk.Frame(cuerpo, bg="white", relief="solid", borderwidth=1)
    marco_med.pack(fill="x", pady=(0, 10))

    tk.Label(
        marco_med,
        text="Prescripción de Medicamento",
        font=("Arial", 11, "bold"),
        bg="white",
        fg="#1F4E79"
    ).pack(anchor="w", padx=15, pady=(10, 5))

    grid_med = tk.Frame(marco_med, bg="white")
    grid_med.pack(fill="x", padx=15, pady=(0, 10))
    grid_med.grid_columnconfigure(0, weight=2)
    grid_med.grid_columnconfigure(1, weight=1)
    grid_med.grid_columnconfigure(2, weight=1)

    tk.Label(
        grid_med,
        text="Medicamento",
        font=("Arial", 9, "bold"),
        bg="white",
        fg="#333333"
    ).grid(row=0, column=0, sticky="w", padx=4)

    tk.Label(
        grid_med,
        text="Días de tratamiento",
        font=("Arial", 9, "bold"),
        bg="white",
        fg="#333333"
    ).grid(row=0, column=1, sticky="w", padx=4)

    tk.Label(
        grid_med,
        text="Horario de suministro",
        font=("Arial", 9, "bold"),
        bg="white",
        fg="#333333"
    ).grid(row=0, column=2, sticky="w", padx=4)

    combo_medicamento = ttk.Combobox(
        grid_med,
        state="readonly" if catalogo_medicamentos else "normal",
        font=("Arial", 10),
        values=[m[1] for m in catalogo_medicamentos]
    )
    combo_medicamento.grid(row=1, column=0, sticky="ew", padx=4, pady=4, ipady=3)
    if catalogo_medicamentos:
        combo_medicamento.current(0)

    entrada_dias = tk.Entry(
        grid_med,
        font=("Arial", 10),
        relief="solid",
        borderwidth=1
    )
    entrada_dias.grid(row=1, column=1, sticky="ew", padx=4, pady=4, ipady=4)
    entrada_dias.insert(0, "7 días")

    entrada_horario = tk.Entry(
        grid_med,
        font=("Arial", 10),
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

    tk.Button(
        grid_med,
        text="Agregar medicamento al diagnóstico",
        command=agregar_tratamiento_al_diagnostico,
        bg="#E8EEF5",
        fg="#1F4E79",
        relief="flat",
        font=("Arial", 9, "bold"),
        cursor="hand2"
    ).grid(row=2, column=0, columnspan=3, sticky="e", padx=4, pady=(4, 0))

    # Botones inferiores
    botones = tk.Frame(cuerpo, bg="#F0F2F5")
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

    tk.Button(
        botones,
        text="Cerrar",
        command=modal.destroy,
        width=14,
        bg="#E0E4E8",
        fg="#333333",
        relief="flat",
        font=("Arial", 10),
        cursor="hand2"
    ).pack(side="left", ipady=5)

    tk.Button(
        botones,
        text="Guardar consulta",
        command=accion_guardar_consulta,
        width=18,
        bg="#1F4E79",
        fg="white",
        relief="flat",
        font=("Arial", 10, "bold"),
        cursor="hand2"
    ).pack(side="right", padx=(6, 0), ipady=5)

    tk.Button(
        botones,
        text="GENERAR RECETA",
        command=accion_generar_receta,
        width=18,
        bg="#2E7D32",
        fg="white",
        activebackground="#1B5E20",
        activeforeground="white",
        relief="flat",
        font=("Arial", 10, "bold"),
        cursor="hand2"
    ).pack(side="right", padx=6, ipady=5)
