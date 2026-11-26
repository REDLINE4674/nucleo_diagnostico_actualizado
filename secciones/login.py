import tkinter as tk
from tkinter import messagebox
import psycopg2

from operaciones_sql.conexion import conectar
from operaciones_sql.consultas import consulta_usuarios
from utilidades.roles import obtener_nombre_perfil
from utilidades.diseno import COLORES, FUENTES, crear_boton, crear_etiqueta, crear_marco, crear_entrada


def mostrar_login(ventana, al_conectar):

    ventana.title("Inicio de sesión")
    ventana.geometry("900x500")
    ventana.resizable(False, False)
    ventana.configure(bg=COLORES["fondo"])

    login = crear_marco(ventana, estilo="tarjeta")

    login.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        width=360,
        height=400
    )

    encabezado = crear_marco(login, estilo="azul", height=100)

    encabezado.pack(fill="x")
    encabezado.pack_propagate(False)

    crear_etiqueta(encabezado, text='NÚCLEO', estilo="encabezado", font=FUENTES['marca']).pack(pady=(20, 3))

    crear_etiqueta(encabezado, text='Sistema de administración de datos', estilo="sobre_azul", font=FUENTES['compacta']).pack()

    formulario = crear_marco(login, estilo="superficie")

    formulario.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=20
    )

    crear_etiqueta(formulario, text='Inicio de sesión', estilo="texto", font=FUENTES['titulo_16']).pack(pady=(0, 20))

    # Usuario
    crear_etiqueta(formulario, text='Usuario', estilo="texto", font=FUENTES['normal_negrita']).pack(anchor="w")

    caja_usuario = crear_entrada(formulario, font=FUENTES['mediana'])

    caja_usuario.pack(
        fill="x",
        pady=(5, 15),
        ipady=6
    )

    # Contraseña
    crear_etiqueta(formulario, text='Contraseña', estilo="texto", font=FUENTES['normal_negrita']).pack(anchor="w")

    caja_password = crear_entrada(formulario, show='*', font=FUENTES['mediana'])

    caja_password.pack(
        fill="x",
        pady=(5, 20),
        ipady=6
    )

    def iniciar_sesion():
        usuario = caja_usuario.get().strip()
        password = caja_password.get()

        if usuario == "" or password == "":
            messagebox.showwarning(
                "Campos vacíos",
                "Ingresa tu usuario y contraseña.",
                parent=ventana
            )
            return

        conexion = None
        try:
            conexion = conectar()
            usuario_valido = consulta_usuarios(conexion, usuario, password)
        except psycopg2.Error:
            if conexion is not None:
                conexion.close()
            messagebox.showerror(
                "Error de conexión",
                "No se pudo conectar con la base de datos.",
                parent=ventana
            )
            return

        if not usuario_valido:
            conexion.close()
            messagebox.showerror(
                "Error de inicio de sesión",
                "Usuario o contraseña incorrectos.",
                parent=ventana
            )
            return

        nombre_usuario, rol = usuario_valido
        perfil = obtener_nombre_perfil(rol)
        messagebox.showinfo(
            "¡Bienvenido!",
            f"Hola, {nombre_usuario}.\nHas iniciado sesión como {perfil}.",
            parent=ventana
        )
        ventana.unbind("<Return>")
        login.destroy()
        al_conectar(conexion, nombre_usuario, rol)

    def cancelar():
        caja_usuario.delete(0, tk.END)
        caja_password.delete(0, tk.END)
        caja_usuario.focus_set()

    botones = crear_marco(formulario, estilo="superficie")

    botones.pack(fill="x")

    crear_boton(botones, text='Cancelar', command=cancelar, estilo="neutro", width=12, activebackground=COLORES["gris_presionado"]).pack(side="left", padx=(0, 5), ipady=5)

    crear_boton(botones, text='Iniciar sesión', command=iniciar_sesion, estilo="principal", width=15, activebackground=COLORES["azul_presionado"], activeforeground=COLORES["blanco"]).pack(side="right", ipady=5)

    ventana.bind("<Return>", lambda event: iniciar_sesion())
    caja_usuario.focus_set()
