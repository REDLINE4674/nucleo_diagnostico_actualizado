"""Inserciones SQL reutilizables."""

from psycopg2 import sql


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
