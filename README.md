# Núcleo de Diagnóstico

Aplicación de escritorio para administrar pacientes, personal, usuarios, citas
médicas, consultas clínicas y recetas. Está desarrollada en Python con Tkinter
y utiliza PostgreSQL para almacenar la información.

## Funcionalidades

- Inicio de sesión y menú con opciones según el rol.
- Consulta de tablas de la base de datos y formularios de captura generados a
  partir de sus columnas.
- Registro de citas, consulta de disponibilidad por médico y fecha, y
  actualización de citas existentes.
- Validación para evitar citas duplicadas del mismo paciente en la misma fecha
  y hora.
- Consulta del historial clínico y registro de diagnósticos y medicamentos.
- Generación de recetas en PDF.
- Asociación de cuentas de usuario con empleados o doctores mediante su ID.

### Roles

| Rol | Acceso |
| --- | --- |
| Administrador (`1`) | Consulta las tablas y puede registrar datos. Puede generar y actualizar citas. |
| Empleado (`2`) | Consulta pacientes, puede registrar pacientes y gestionar citas. |
| Doctor (`3`) | Consulta sus citas, los pacientes relacionados con ellas y sus consultas; puede registrar consultas y recetas. |

El acceso a pacientes y consultas de un doctor se filtra por el doctor asociado
a su cuenta.

## Requisitos

- Windows con Python instalado y Tkinter disponible.
- PostgreSQL y una base de datos accesible desde la aplicación.
- Paquetes de Python:
  - `psycopg2-binary` para conectarse a PostgreSQL.
  - `Pillow` para mostrar el logotipo opcional en la interfaz.
  - `reportlab` para generar recetas en PDF.

Este proyecto no incluye un archivo `requirements.txt` ni fija versiones de
los paquetes.

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

Configura primero PostgreSQL siguiendo la sección siguiente. Después ejecuta:

```powershell
python main.py
```

La ventana de inicio de sesión es el punto de entrada. Al cerrar sesión, la
conexión actual se cierra y se muestra nuevamente el inicio de sesión.

## Configuración de PostgreSQL

La conexión se configura mediante constantes en `conexion.py`. Ajusta el host,
el nombre de la base de datos, el puerto y las credenciales para tu instalación
local. No publiques credenciales reales ni las guardes en el repositorio.

La aplicación espera que exista el esquema `public` y que estén creadas las
tablas base:

- `usuarios`
- `empleado`
- `doctor`
- `paciente`
- `cita`

El programa consulta las tablas de la base de datos al construir el menú. Por
eso, los nombres y columnas de las tablas deben corresponder al esquema que
espera cada función.

### Scripts SQL incluidos

Ejecuta los scripts desde un cliente PostgreSQL, conectado a la base de datos
del proyecto:

1. `ATUALIZACION DE USUARIOS.sql`: agrega las columnas `id_empleado` y
   `id_doctor` si faltan, establece sus claves foráneas y evita que una cuenta
   esté vinculada simultáneamente a un empleado y a un doctor. Requiere que las
   tablas `usuarios`, `empleado` y `doctor` ya existan.
2. `tablas_consulta_medicamento.sql`: crea `medicamento` y `consulta`. Debe
   ejecutarse después de crear `cita`, pues `consulta` referencia
   `cita(id_cita)`.

Los scripts usan `IF NOT EXISTS` o verificaciones de restricciones, por lo que
PostgreSQL puede informar que una columna ya existe y omitirla. Ese aviso es
normal cuando la actualización ya se aplicó.

### Tablas principales

| Tabla | Uso |
| --- | --- |
| `usuarios` | Inicio de sesión, rol y vínculo opcional con empleado o doctor. Roles: administrador `1`, empleado `2`, doctor `3`. |
| `empleado` | Datos del personal y turno. |
| `doctor` | Datos del doctor y especialidad. |
| `paciente` | Datos de los pacientes. |
| `cita` | Paciente, doctor, fecha y hora de cada cita. |
| `medicamento` | Catálogo de medicamentos, presentación, vía y caducidad. |
| `consulta` | Diagnóstico asociado a una cita y, opcionalmente, un medicamento. |

## Estructura del proyecto

| Archivo | Responsabilidad |
| --- | --- |
| `main.py` | Crea la ventana principal y coordina inicio/cierre de sesión. |
| `login.py` | Interfaz de acceso y validación de credenciales. |
| `menu.py` | Menú principal, navegación, permisos por rol y vistas de tablas. |
| `conexion.py` | Conexión PostgreSQL, lectura de esquema, consulta e inserción de registros. |
| `consultas.py` | Presenta los registros consultados en una tabla visual. |
| `insertar.py` | Construye formularios de captura; para usuarios ofrece IDs según el rol. |
| `consultas_citas.py` | Consultas y operaciones de base de datos relacionadas con citas y doctores. |
| `citas.py` | Formularios de citas, calendario, consulta y actualización desde la interfaz. |
| `consultas_medicas.py` | Historial clínico, diagnósticos, medicamentos y generación de recetas PDF. |
| `ATUALIZACION DE USUARIOS.sql` | Actualiza los vínculos entre cuentas, empleados y doctores. |
| `tablas_consulta_medicamento.sql` | Crea las tablas de medicamentos y consultas. |

## Archivos opcionales

La interfaz y el PDF intentan cargar `imagenes/nd.png` como logotipo. Si el
archivo no está disponible, la interfaz muestra un encabezado de texto y la
receta se genera sin logotipo.

Las recetas se guardan como `receta.pdf` en el directorio de trabajo desde el
que se ejecutó la aplicación.

## Consideraciones

- No se incluye un script completo para crear todas las tablas base; prepara
  primero el esquema PostgreSQL requerido y luego aplica los scripts incluidos.
- Actualmente las credenciales de conexión se configuran en `conexion.py`.
- La autenticación compara la contraseña almacenada con el valor ingresado; el
  proyecto no implementa hash de contraseñas. No se recomienda usarlo con
  credenciales reales sin incorporar almacenamiento seguro de contraseñas.
- No se incluye una suite de pruebas automatizadas.
