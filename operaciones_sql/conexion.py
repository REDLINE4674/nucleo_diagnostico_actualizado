"""Configuracion y conexion a PostgreSQL."""

import psycopg2


# Datos de conexion
HOST = "localhost"
DATABASE = "NucleoDeDiagnostico"
PORT = "5433"
USUARIO = "admin"
PASSWORD = "1234"


def conectar():
    conexion = psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USUARIO,
        password=PASSWORD,
        port=PORT
    )
    return conexion
