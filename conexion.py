import psycopg2
from psycopg2 import sql


# Datos de conexión
HOST = "localhost"
DATABASE = "NucleoDeDiagnostico"
PORT = "5433"
USUARIO = "admin"
PASSWORD = "1234"


# Conectar a PostgreSQL
def conectar():
    conexion = psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USUARIO,
        password=PASSWORD,
        port=PORT
    )
    return conexion


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


# Obtener las tablas de la base de datos
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


# Consultar los registros de una tabla
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


# Obtener las columnas que se pueden insertar
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


# Insertar un registro
def insertar_registro(conexion, nombre_tabla, nombres, valores):
    cursor = conexion.cursor()

    if nombres:
        consulta = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(nombre_tabla),
            sql.SQL(", ").join(
                map(sql.Identifier, nombres)
            ),
            sql.SQL(", ").join(
                sql.Placeholder() for valor in valores
            )
        )
        cursor.execute(consulta, valores)
    else:
        consulta = sql.SQL("INSERT INTO {} DEFAULT VALUES").format(
            sql.Identifier(nombre_tabla)
        )
        cursor.execute(consulta)

    conexion.commit()
    cursor.close()
