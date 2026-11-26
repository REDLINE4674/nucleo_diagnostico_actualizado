"""Consultas y operaciones SQL del historial cl?nico."""

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
