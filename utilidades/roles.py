def obtener_nombre_perfil(rol):
    perfiles = {
        "1": "Administrador",
        "2": "Empleado",
        "3": "Doctor"
    }
    return perfiles.get(str(rol), "Rol no definido")
