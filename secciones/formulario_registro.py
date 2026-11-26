import tkinter as tk
from tkinter import ttk, messagebox

from operaciones_sql.consultas import (
    obtener_columnas,
    obtener_personal_por_rol
)
from operaciones_sql.insertar import insertar_registro
from utilidades.diseno import COLORES, FUENTES, crear_boton, crear_etiqueta, crear_marco, crear_entrada, crear_combobox


def abrir_ventana_insertar(ventana, conexion, nombre_tabla, actualizar):

    estilo = None
    tema_anterior = None
    es_tabla_usuarios = str(nombre_tabla).strip().lower() in (
        "usuario",
        "usuarios"
    )

    try:

        columnas = obtener_columnas(conexion, nombre_tabla)
        columnas_normalizadas = {
            columna[0].lower() for columna in columnas
        }

        if es_tabla_usuarios and not {
            "id_doctor",
            "id_empleado"
        }.issubset(columnas_normalizadas):
            raise RuntimeError(
                "La tabla usuarios debe incluir las columnas id_doctor e "
                "id_empleado. Ejecuta la migración "
                "'migracion_usuarios_id_empleado.sql' antes de crear usuarios."
            )

        # CONFIGURACION DE LA VENTANA

        nueva = tk.Toplevel(ventana)

        nueva.title("Nuevo registro")
        nueva.geometry("450x600")
        nueva.resizable(False, False)

        nueva.configure(bg=COLORES["fondo"])

        nueva.transient(ventana)
        nueva.grab_set()

        # Estilos
        estilo = ttk.Style(nueva)
        tema_anterior = estilo.theme_use()
        estilo.theme_use("clam")

        estilo.configure(
            "Formulario.TCombobox",
            padding=(0, 0),
            font=FUENTES["normal"],
            fieldbackground=COLORES["blanco"],
            foreground=COLORES["texto"],
            background=COLORES["blanco"],
            bordercolor="#333333",
            lightcolor="#333333",
            darkcolor="#333333",
            borderwidth=1,
            relief="solid"
        )
        estilo.map(
            "Formulario.TCombobox",
            fieldbackground=[("readonly", "white")],
            foreground=[("readonly", "#333333")]
        )

        def cerrar():
            nueva.destroy()
            estilo.theme_use(tema_anterior)

        nueva.protocol("WM_DELETE_WINDOW", cerrar)

        # ENCABEZADO

        encabezado = crear_marco(nueva, estilo="azul", height=85)

        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)

        crear_etiqueta(encabezado, text='Nuevo registro', estilo="encabezado").pack(anchor="w", padx=20, pady=(15, 2))

        crear_etiqueta(encabezado, text=f'Tabla: {nombre_tabla.capitalize()}', estilo="sobre_azul").pack(anchor="w", padx=20)

        # CONTENEDOR DEL FORMULARIO

        contenedor = crear_marco(nueva, estilo="fondo")

        contenedor.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=12
        )

        canvas = tk.Canvas(
            contenedor,
            bg=COLORES["blanco"],
            highlightthickness=0
        )

        scroll = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=canvas.yview
        )

        formulario = crear_marco(canvas, estilo="superficie")

        ventana_formulario = canvas.create_window(
            (0, 0),
            window=formulario,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scroll.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scroll.pack(
            side="right",
            fill="y"
        )

        def ajustar_formulario(event):
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        def ajustar_ancho(event):
            canvas.itemconfigure(
                ventana_formulario,
                width=event.width
            )

        formulario.bind(
            "<Configure>",
            ajustar_formulario
        )

        canvas.bind(
            "<Configure>",
            ajustar_ancho
        )

        def desplazar_formulario(event):
            canvas.yview_scroll(int(-event.delta / 120), "units")

        nueva.bind("<MouseWheel>", desplazar_formulario)

        # CAMPOS DEL FORMULARIO

        entradas = {}
        entrada_rol = None
        entrada_id = None
        selector_id_creado = False

        for columna in columnas:

            nombre_columna = columna[0]
            nombre_normalizado = nombre_columna.lower()
            es_columna_id_usuario = (
                es_tabla_usuarios
                and nombre_normalizado in ("id_doctor", "id_empleado")
            )

            if es_columna_id_usuario and selector_id_creado:
                continue

            if es_columna_id_usuario:
                selector_id_creado = True

            campo = crear_marco(formulario, estilo="superficie")

            campo.pack(
                fill="x",
                padx=20,
                pady=9
            )
            campo.grid_columnconfigure(0, minsize=150)
            campo.grid_columnconfigure(1, weight=1)
            campo.grid_rowconfigure(0, minsize=30)

            crear_etiqueta(campo, text='Id' if es_columna_id_usuario else nombre_columna.replace('_', ' ').capitalize(), estilo="texto", font=FUENTES['normal_negrita'], anchor='w', wraplength=130).grid(row=0, column=0, sticky="w", padx=(0, 12))

            if nombre_normalizado == "sexo":

                entrada = crear_combobox(campo, values=['F', 'M'], state='readonly', style='Formulario.TCombobox')
                entrada.set("")

            elif nombre_normalizado == "turno":

                entrada = crear_combobox(campo, values=['M', 'V'], state='readonly', style='Formulario.TCombobox')
                entrada.set("")

            elif es_tabla_usuarios and nombre_normalizado == "rol":

                entrada = crear_combobox(campo, values=['admin', 'empleado', 'doctor'], state='readonly', style='Formulario.TCombobox')
                entrada.set("empleado")
                entrada_rol = entrada

            elif es_columna_id_usuario:

                entrada = crear_combobox(campo, values=[], state='readonly', style='Formulario.TCombobox')
                entrada_id = entrada

            else:

                entrada = crear_entrada(campo)

            entrada.grid(
                row=0,
                column=1,
                sticky="nsew",
                ipady=5
            )

            entradas[nombre_columna] = entrada

        opciones_por_rol = {
            rol: obtener_personal_por_rol(conexion, rol)
            for rol in ("empleado", "doctor")
        } if es_tabla_usuarios else {}
        ids_por_opcion = {}

        if es_tabla_usuarios:
            def actualizar_opciones_id(event=None):
                rol = entrada_rol.get().strip().lower()
                registros = opciones_por_rol.get(rol, [])
                ids_por_opcion.clear()
                opciones = []

                for id_personal, nombre in registros:
                    opcion = f"{id_personal} - {nombre}"
                    opciones.append(opcion)
                    ids_por_opcion[opcion] = id_personal

                entrada_id.configure(values=opciones)
                entrada_id.set("")
                entrada_id.configure(
                    state="readonly" if opciones else "disabled"
                )

            entrada_rol.bind(
                "<<ComboboxSelected>>",
                actualizar_opciones_id
            )
            actualizar_opciones_id()

        def cancelar():
            cerrar()

        def guardar():

            nombres = []
            valores = []

            rol_usuario = (
                entrada_rol.get().strip().lower()
                if es_tabla_usuarios
                else None
            )

            if es_tabla_usuarios and rol_usuario in ("empleado", "doctor"):
                opcion_seleccionada = entrada_id.get()
                if opcion_seleccionada not in ids_por_opcion:
                    messagebox.showwarning(
                        "Registro requerido",
                        "Selecciona un empleado o doctor registrado para "
                        "el rol elegido.",
                        parent=nueva
                    )
                    return

            for columna in columnas:

                nombre_columna = columna[0]
                nombre_normalizado = nombre_columna.lower()

                if es_tabla_usuarios and nombre_normalizado in (
                    "id_doctor",
                    "id_empleado"
                ):
                    continue

                valor = entradas[nombre_columna].get().strip()

                if valor != "":

                    if es_tabla_usuarios and nombre_normalizado == "rol":
                        roles = {
                            "admin": 1,
                            "empleado": 2,
                            "user": 2,
                            "doctor": 3
                        }
                        if valor.lower() not in roles:
                            messagebox.showwarning(
                                "Rol requerido",
                                "Selecciona admin, empleado o doctor.",
                                parent=nueva
                            )
                            return
                        valor = roles[valor.lower()]

                    nombres.append(nombre_columna)
                    valores.append(valor)

            if es_tabla_usuarios and rol_usuario in ("empleado", "doctor"):
                columna_id = (
                    "id_empleado" if rol_usuario == "empleado"
                    else "id_doctor"
                )
                nombres.append(columna_id)
                valores.append(ids_por_opcion[entrada_id.get()])

            try:

                insertar_registro(
                    conexion,
                    nombre_tabla,
                    nombres,
                    valores
                )

                messagebox.showinfo(
                    "Registro insertado",
                    "El registro se insertó correctamente.",
                    parent=nueva
                )

                cerrar()
                actualizar()

            except Exception as error:

                conexion.rollback()

                messagebox.showerror(
                    "Error al insertar",
                    str(error),
                    parent=nueva
                )

        # Botones

        botones = crear_marco(nueva, estilo="fondo")

        botones.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        crear_boton(botones, text='Cancelar', command=cancelar, estilo="neutro", width=15).pack(side="left")

        crear_boton(botones, text='Guardar registro', command=guardar, estilo="principal", width=18, activebackground=COLORES["azul_presionado"], activeforeground=COLORES["blanco"]).pack(side="right")

    except Exception as error:

        if estilo is not None and tema_anterior is not None:
            estilo.theme_use(tema_anterior)

        messagebox.showerror(
            "Error",
            "No se pudo abrir el formulario.\n\n" + str(error)
        )
