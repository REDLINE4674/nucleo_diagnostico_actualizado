import tkinter as tk
from secciones.login import mostrar_login
from interfaz.menu import mostrar_menu


def main():
    ventana = tk.Tk()
    ventana.title("Nucleo de Diagnostico")
    ventana.geometry("1000x600")

    conexion_actual = None

    def iniciar_aplicacion(conexion, usuario, rol):
        mostrar_menu(
            ventana,
            conexion,
            usuario,
            rol,
            cerrar_sesion
        )

    def cerrar_aplicacion():
        if conexion_actual:
            conexion_actual.close()
        ventana.destroy()

    def cerrar_sesion():
        nonlocal conexion_actual

        if conexion_actual:
            conexion_actual.close()
            conexion_actual = None

        for widget in ventana.winfo_children():
            widget.destroy()

        mostrar_login(
            ventana,
            conexion_exitosa
        )

    def conexion_exitosa(conexion, usuario, rol):
        nonlocal conexion_actual
        conexion_actual = conexion
        iniciar_aplicacion(conexion, usuario, rol)

    ventana.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
    mostrar_login(ventana, conexion_exitosa)
    ventana.mainloop()


if __name__ == "__main__":
    main()
