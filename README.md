# Núcleo de Diagnóstico

Aplicación de escritorio para administrar pacientes, personal, usuarios, citas,
consultas clínicas y recetas. Está desarrollada en Python con Tkinter y utiliza
PostgreSQL para almacenar la información.

## Funcionalidades

- Inicio de sesión y menú con opciones según el rol.
- Consulta de tablas y formularios de captura generados desde sus columnas.
- Registro, consulta y actualización de citas, con validación de disponibilidad.
- Validación para evitar citas duplicadas del mismo paciente en la misma fecha y hora.
- Consulta del historial clínico y registro de diagnósticos y medicamentos.
- Generación de recetas en PDF.
- Asociación de cuentas de usuario con empleados o doctores mediante su ID.

### Roles

| Rol | Acceso |
| --- | --- |
| Administrador (`1`) | Consulta tablas, registra datos y gestiona citas. |
| Empleado (`2`) | Consulta y registra pacientes; gestiona citas. |
| Doctor (`3`) | Consulta sus citas, pacientes e historial; registra consultas y recetas. |

El acceso de cada doctor a pacientes y consultas se filtra por el doctor asociado a
su cuenta.

## Requisitos

- Windows con Python y Tkinter.
- PostgreSQL y una base de datos accesible desde la aplicación.
- Paquetes: `psycopg2-binary`, `Pillow` y `reportlab`.

El proyecto no incluye `requirements.txt` ni fija versiones de los paquetes.

## Instalación y ejecución

Abre PowerShell en la carpeta del proyecto y crea/activa un entorno virtual:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```powershell
python -m pip install --upgrade pip
python -m pip install psycopg2-binary Pillow reportlab
```

Configura PostgreSQL y ejecuta la aplicación desde la carpeta del proyecto:

```powershell
python main.py
```

La ventana de inicio de sesión es el punto de entrada. Al cerrar sesión, la
conexión se cierra y vuelve a mostrarse el inicio de sesión.

## Configuración de PostgreSQL

Ajusta las constantes de conexión en `operaciones_sql/conexion.py`. Configura el
host, el nombre de la base de datos, el puerto y las credenciales locales. No
publiques credenciales reales ni las guardes en el repositorio.

La aplicación espera el esquema `public` y las tablas base `usuarios`, `empleado`,
`doctor`, `paciente` y `cita`. Sus nombres y columnas deben corresponder a los que
consulta el programa.

### Scripts SQL incluidos

Ejecuta los scripts desde un cliente PostgreSQL conectado a la base de datos del
proyecto:

1. `database/TABLA CITAS.sql`: crea `cita` y sus relaciones con `"Paciente"(codigo)`
   y `"Doctor"(id)`. Estas tablas deben existir antes de ejecutar el script.
   También agrega restricciones para evitar citas duplicadas del mismo paciente o
   doctor en la misma fecha y hora.
2. `database/tablas_consulta_medicamento.sql`: crea `medicamento` y `consulta`.
   Ejecuta este script después de crear `cita`, porque `consulta` la referencia.
3. `database/ATUALIZACION DE USUARIOS.sql`: agrega `id_empleado` e `id_doctor`,
   establece sus claves foráneas y evita que una cuenta se vincule a ambos tipos de
   personal. Requiere que existan `usuarios`, `empleado` y `doctor`.

Los scripts comprueban si algunos objetos ya existen. Los avisos de objetos
existentes son normales si la actualización ya se aplicó.

### Tablas principales

| Tabla | Uso |
| --- | --- |
| `usuarios` | Inicio de sesión, rol y vínculo opcional con empleado o doctor. |
| `empleado` | Datos del personal y turno. |
| `doctor` | Datos del doctor y especialidad. |
| `paciente` | Datos de los pacientes. |
| `cita` | Paciente, doctor, fecha y hora de cada cita. |
| `medicamento` | Catálogo de medicamentos, presentación, vía y caducidad. |
| `consulta` | Diagnóstico asociado a una cita y, opcionalmente, un medicamento. |

## Estructura del proyecto

Las vistas de las páginas están en `secciones/`. `interfaz/menu.py` administra la
navegación y los permisos, y conecta cada opción con su vista.

```text
main.py                       Punto de entrada
interfaz/                     Marco principal y navegación
  menu.py                     Navegación y control de permisos
secciones/                    Vistas y flujos de cada página
  login.py                    Inicio de sesión
  inicio.py                   Página principal
  citas.py                    Página y formularios de citas
  registros.py                Tablas y consultas por rol
  diagnosticos.py             Consulta clínica e historial
  formulario_registro.py      Formulario de alta de registros
operaciones_sql/              Conexión y operaciones con PostgreSQL
  conexion.py                 Configuración y conexión
  consultas.py                Consultas generales y metadatos
  citas.py                    Operaciones de citas y médicos
  consultas_medicas.py        Historial, pacientes y medicamentos
  insertar.py                 Inserción de registros
utilidades/                   Funciones compartidas
  diseno.py                   Diseño y constructores reutilizables de Tkinter
  roles.py                    Etiquetas de perfil
  recetas.py                  Generación de recetas PDF
database/                     Scripts SQL de actualización y creación
  TABLA CITAS.sql             Creación de citas y restricciones de duplicados
  ATUALIZACION DE USUARIOS.sql Vínculos de cuentas con empleados y doctores
  tablas_consulta_medicamento.sql Tablas de medicamentos y consultas
```

## Sistema de diseño

`utilidades/diseno.py` centraliza los colores (`COLORES`), las tipografías
(`FUENTES`) y los estilos comunes de la interfaz. También ofrece constructores
para botones, etiquetas, marcos, entradas, selectores, encabezados de sección y
tablas con barras de desplazamiento.

Usa los constructores en las vistas para mantener los estilos compartidos. El
parámetro `estilo` permite elegir variantes, y las opciones adicionales permiten
ajustes propios de cada control:

```python
from utilidades.diseno import crear_boton, crear_etiqueta

crear_etiqueta(contenedor, text="Pacientes", estilo="titulo")
crear_boton(
    contenedor,
    text="Guardar",
    command=guardar,
    estilo="principal"
)
```

Para cambiar la apariencia general, modifica `COLORES`, `FUENTES` o los mapas de
estilos en `utilidades/diseno.py`.

## Archivos opcionales

La interfaz y el PDF intentan cargar `imagenes/nd.png` como logotipo. Si el archivo
no está disponible, se muestra un encabezado de texto y la receta se genera sin
logotipo.

Las recetas se guardan como `receta.pdf` en el directorio de trabajo desde el que
se ejecutó la aplicación.

## Consideraciones

- No se incluye un script completo para crear todas las tablas base; prepara el
  esquema PostgreSQL requerido y luego aplica los scripts incluidos.
- La autenticación compara la contraseña almacenada con el valor ingresado. El
  proyecto no implementa hash de contraseñas y no se recomienda usarlo con
  credenciales reales sin incorporar almacenamiento seguro.
- El proyecto no incluye una suite de pruebas automatizadas.
