"""Lectura de datos y metadatos de PostgreSQL."""

from psycopg2 import sql


def _obtener_columnas_clave_primaria(cursor, nombre_tabla):
    cursor.execute("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints AS tc
        INNER JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
            AND tc.table_name = kcu.table_name
        WHERE tc.table_schema = 'public'
        AND tc.table_name = %s
        AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY kcu.ordinal_position ASC
    """, (nombre_tabla,))
    return [columna[0] for columna in cursor.fetchall()]


def obtener_tablas(conexion):
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)

    tablas = cursor.fetchall()
    cursor.close()
    return tablas


def consultar_registros(conexion, nombre_tabla):
    cursor = conexion.cursor()

    try:
        columnas_clave = _obtener_columnas_clave_primaria(
            cursor,
            nombre_tabla
        )
        if not columnas_clave:
            raise ValueError(
                f"La tabla '{nombre_tabla}' no tiene una clave primaria "
                "para ordenar los registros por ID."
            )

        orden = sql.SQL(", ").join(
            sql.SQL("{} ASC").format(sql.Identifier(columna))
            for columna in columnas_clave
        )
        consulta = sql.SQL("SELECT * FROM {} ORDER BY {}").format(
            sql.Identifier(nombre_tabla),
            orden
        )

        cursor.execute(consulta)
        columnas = [columna[0] for columna in cursor.description]
        registros = cursor.fetchall()
        return columnas, registros

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()


def obtener_columnas(conexion, nombre_tabla):
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = %s
        AND is_generated = 'NEVER'
        AND is_identity = 'NO'
        ORDER BY ordinal_position
    """, (nombre_tabla,))

    columnas = cursor.fetchall()
    cursor.close()
    return columnas


def consulta_usuarios(conexion, nombre, contrasena):
    cursor = conexion.cursor()
    try:
        columnas_clave = _obtener_columnas_clave_primaria(
            cursor,
            "usuarios"
        )
        if not columnas_clave:
            raise ValueError(
                "La tabla 'usuarios' no tiene una clave primaria "
                "para ordenar por ID."
            )

        orden = sql.SQL(", ").join(
            sql.SQL("{} ASC").format(sql.Identifier(columna))
            for columna in columnas_clave
        )
        consulta = sql.SQL("""
            SELECT nombre, rol
            FROM usuarios
            WHERE nombre = %s AND contrasena = %s
            ORDER BY {}
        """).format(orden)
        cursor.execute(consulta, (nombre, contrasena))
        return cursor.fetchone()
    finally:
        cursor.close()


def obtener_personal_por_rol(conexion, rol):
    tablas_por_rol = {
        "empleado": ("empleado", "id_empleado"),
        "doctor": ("doctor", "id_doctor")
    }
    nombre_tabla, columna_id = tablas_por_rol[rol]
    cursor = conexion.cursor()

    try:
        cursor.execute(
            f"SELECT {columna_id}, nombre FROM {nombre_tabla} "
            f"ORDER BY {columna_id} ASC"
        )
        return cursor.fetchall()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
