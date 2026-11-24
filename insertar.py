import tkinter as tk
from tkinter import ttk, messagebox

from conexion import obtener_columnas, insertar_registro


def _obtener_personal(conexion, rol):
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

        nueva.configure(bg="#F0F2F5")

        nueva.transient(ventana)
        nueva.grab_set()

        # Estilos
        estilo = ttk.Style(nueva)
        tema_anterior = estilo.theme_use()
        estilo.theme_use("clam")

        estilo.configure(
            "Formulario.TCombobox",
            padding=(0, 0),
            font=("Arial", 10),
            fieldbackground="white",
            foreground="#333333",
            background="white",
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

        encabezado = tk.Frame(
            nueva,
            bg="#1F4E79",
            height=85
        )

        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)

        tk.Label(
            encabezado,
            text="Nuevo registro",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#1F4E79"
        ).pack(anchor="w", padx=20, pady=(15, 2))

        tk.Label(
            encabezado,
            text=f"Tabla: {nombre_tabla.capitalize()}",
            font=("Arial", 10),
            fg="#DCE8F5",
            bg="#1F4E79"
        ).pack(anchor="w", padx=20)

        # CONTENEDOR DEL FORMULARIO

        contenedor = tk.Frame(
            nueva,
            bg="#F0F2F5"
        )

        contenedor.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=12
        )

        canvas = tk.Canvas(
            contenedor,
            bg="white",
            highlightthickness=0
        )

        scroll = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=canvas.yview
        )

        formulario = tk.Frame(
            canvas,
            bg="white"
        )

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

            campo = tk.Frame(
                formulario,
                bg="white"
            )

            campo.pack(
                fill="x",
                padx=20,
                pady=9
            )
            campo.grid_columnconfigure(0, minsize=150)
            campo.grid_columnconfigure(1, weight=1)
            campo.grid_rowconfigure(0, minsize=30)

            tk.Label(
                campo,
                text=(
                    "Id" if es_columna_id_usuario
                    else nombre_columna.replace("_", " ").capitalize()
                ),
                font=("Arial", 10, "bold"),
                bg="white",
                fg="#333333",
                anchor="w",
                wraplength=130
            ).grid(row=0, column=0, sticky="w", padx=(0, 12))

            if nombre_normalizado == "sexo":

                entrada = ttk.Combobox(
                    campo,
                    values=["F", "M"],
                    state="readonly",
                    font=("Arial", 10),
                    style="Formulario.TCombobox"
                )
                entrada.set("")

            elif nombre_normalizado == "turno":

                entrada = ttk.Combobox(
                    campo,
                    values=["M", "V"],
                    state="readonly",
                    font=("Arial", 10),
                    style="Formulario.TCombobox"
                )
                entrada.set("")

            elif es_tabla_usuarios and nombre_normalizado == "rol":

                entrada = ttk.Combobox(
                    campo,
                    values=["admin", "empleado", "doctor"],
                    state="readonly",
                    font=("Arial", 10),
                    style="Formulario.TCombobox"
                )
                entrada.set("empleado")
                entrada_rol = entrada

            elif es_columna_id_usuario:

                entrada = ttk.Combobox(
                    campo,
                    values=[],
                    state="readonly",
                    font=("Arial", 10),
                    style="Formulario.TCombobox"
                )
                entrada_id = entrada

            else:

                entrada = tk.Entry(
                    campo,
                    font=("Arial", 10),
                    relief="solid",
                    borderwidth=1
                )

            entrada.grid(
                row=0,
                column=1,
                sticky="nsew",
                ipady=5
            )

            entradas[nombre_columna] = entrada

        opciones_por_rol = {
            rol: _obtener_personal(conexion, rol)
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

        botones = tk.Frame(
            nueva,
            bg="#F0F2F5"
        )

        botones.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        tk.Button(
            botones,
            text="Cancelar",
            command=cancelar,
            width=15,
            bg="#E0E4E8",
            fg="#333333",
            relief="flat",
            font=("Arial", 10),
            cursor="hand2"
        ).pack(side="left")

        tk.Button(
            botones,
            text="Guardar registro",
            command=guardar,
            width=18,
            bg="#1F4E79",
            fg="white",
            activebackground="#163A5A",
            activeforeground="white",
            relief="flat",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(side="right")

    except Exception as error:

        if estilo is not None and tema_anterior is not None:
            estilo.theme_use(tema_anterior)

        messagebox.showerror(
            "Error",
            "No se pudo abrir el formulario.\n\n" + str(error)
        )
