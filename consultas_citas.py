from datetime import date, datetime


class CitaDuplicadaError(Exception):
    def __init__(self, doctor, fecha, hora):
        fecha_texto = fecha.strftime("%d/%m/%Y")
        hora_texto = hora.strftime("%I:%M %p")
        super().__init__(
            "Este paciente ya tiene una cita registrada con el doctor "
            f"{doctor} el {fecha_texto} a las {hora_texto}. "
            "Selecciona otro horario."
        )


def _obtener_cita_paciente(
    cursor,
    id_paciente,
    fecha,
    hora,
    id_cita_excluir=None
):
    consulta = """
        SELECT d.nombre, c.fecha, c.hora
        FROM cita c
        INNER JOIN doctor d
            ON c.id_doctor = d.id_doctor
        WHERE c.id_paciente = %s
        AND c.fecha = %s
        AND c.hora = %s
    """
    parametros = [id_paciente, fecha, hora]

    if id_cita_excluir is not None:
        consulta += " AND c.id_cita <> %s"
        parametros.append(id_cita_excluir)

    consulta += " ORDER BY c.id_cita ASC LIMIT 1"
    cursor.execute(consulta, tuple(parametros))
    return cursor.fetchone()


def obtener_doctor_por_usuario(conexion, nombre_usuario):
    cursor = conexion.cursor()
    try:
        # 1. Verificar si la tabla usuarios tiene columna id_doctor vinculada
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'usuarios'
                AND column_name = 'id_doctor'
            );
        """)
        tiene_col_id_doctor = cursor.fetchone()[0]

        if tiene_col_id_doctor:
            cursor.execute("""
                SELECT d.id_doctor, d.nombre, d.especialidad
                FROM usuarios u
                INNER JOIN doctor d
                    ON u.id_doctor = d.id_doctor
                WHERE LOWER(TRIM(u.nombre)) = LOWER(TRIM(%s))
                LIMIT 1;
            """, (nombre_usuario,))
            doctor = cursor.fetchone()
            if doctor is not None:
                return doctor

        # 2. Coincidencia exacta por nombre (ignorando prefijo Dr. / Dra.)
        cursor.execute("""
            SELECT id_doctor, nombre, especialidad
            FROM doctor
            WHERE LOWER(TRIM(nombre)) = LOWER(TRIM(%s))
               OR LOWER(TRIM(REGEXP_REPLACE(nombre, '^(dr\\.?|dra\\.?)\\s+', '', 'i')))
                  = LOWER(TRIM(REGEXP_REPLACE(%s, '^(dr\\.?|dra\\.?)\\s+', '', 'i')))
            ORDER BY id_doctor ASC
            LIMIT 1;
        """, (nombre_usuario, nombre_usuario))
        return cursor.fetchone()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()


# Obtener pacientes

def obtener_pacientes(conexion):
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            SELECT id_paciente, nombre
            FROM paciente
            ORDER BY id_paciente ASC;
        """)
        return cursor.fetchall()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()


# Obtener medicos

def obtener_medicos(conexion):
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            SELECT id_doctor, nombre, especialidad
            FROM doctor
            ORDER BY id_doctor ASC;
        """)
        return cursor.fetchall()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()


# Obtener horas disponibles

def obtener_horarios_disponibles(
    conexion,
    id_medico,
    fecha,
    id_cita_excluir=None
):
    horarios = [
        '09:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '01:00 PM',
        '04:00 PM', '05:00 PM', '06:00 PM', '07:00 PM'
    ]
    cursor = conexion.cursor()
    try:
        if id_cita_excluir is not None:
            cursor.execute("""
                SELECT hora
                FROM cita
                WHERE id_doctor = %s
                AND fecha = %s
                AND id_cita <> %s
                ORDER BY id_cita ASC;
            """, (id_medico, fecha, id_cita_excluir))
        else:
            cursor.execute("""
                SELECT hora
                FROM cita
                WHERE id_doctor = %s
                AND fecha = %s
                ORDER BY id_cita ASC;
            """, (id_medico, fecha))
        ocupados = cursor.fetchall()
        horarios_ocupados = [
            h[0].strftime("%I:%M %p")
            for h in ocupados
        ]
        disponibles = [
            h for h in horarios
            if h not in horarios_ocupados
        ]
        return disponibles
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()


# Registrar cita

def registrar_cita(
    conexion,
    id_paciente,
    id_medico,
    fecha,
    hora
):
    cursor = conexion.cursor()
    try:
        cita_existente = _obtener_cita_paciente(
            cursor,
            id_paciente,
            fecha,
            hora
        )
        if cita_existente is not None:
            raise CitaDuplicadaError(*cita_existente)

        cursor.execute("""
            INSERT INTO cita (
                id_paciente,
                id_doctor,
                fecha,
                hora
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id_cita;
        """, (
            id_paciente,
            id_medico,
            fecha,
            hora
        ))
        id_cita = cursor.fetchone()[0]
        conexion.commit()
        return id_cita
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()


# Consultar citas

def obtener_citas(conexion, id_doctor=None):
    cursor = conexion.cursor()
    try:
        consulta = """
            SELECT
                c.id_cita,
                p.nombre AS Paciente,
                m.nombre AS Doctor,
                c.fecha,
                c.hora
            FROM cita c
            INNER JOIN paciente p
                ON c.id_paciente = p.id_paciente
            INNER JOIN doctor m
                ON c.id_doctor = m.id_doctor
        """
        parametros = []
        if id_doctor is not None:
            consulta += " WHERE c.id_doctor = %s"
            parametros.append(id_doctor)

        consulta += " ORDER BY c.id_cita ASC;"
        cursor.execute(consulta, tuple(parametros))
        return cursor.fetchall()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()


# Obtener cita especifica

def obtener_cita(conexion, id_cita):
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            SELECT
                id_paciente,
                id_doctor,
                fecha,
                hora
            FROM cita
            WHERE id_cita = %s
            ORDER BY id_cita ASC;
        """, (id_cita,))
        return cursor.fetchone()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()


# Actualizar cita

def actualizar_cita(conexion, id_cita, id_medico, fecha, hora):
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            SELECT id_paciente
            FROM cita
            WHERE id_cita = %s
            ORDER BY id_cita ASC;
        """, (id_cita,))
        registro_actual = cursor.fetchone()

        if registro_actual is not None:
            cita_existente = _obtener_cita_paciente(
                cursor,
                registro_actual[0],
                fecha,
                hora,
                id_cita
            )
            if cita_existente is not None:
                raise CitaDuplicadaError(*cita_existente)

        cursor.execute("""
            UPDATE cita
            SET id_doctor = %s,
                fecha = %s,
                hora = %s
            WHERE id_cita = %s;
        """, (id_medico, fecha, hora, id_cita))

        if cursor.rowcount == 0:
            raise Exception("No se encontró la cita seleccionada.")

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
