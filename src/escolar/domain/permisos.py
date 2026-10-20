from escolar.domain.entities import Rol

_PERMISOS_POR_ROL: dict[Rol, tuple[str, ...]] = {
    Rol.ADMIN: (
        "usuarios",
        "estudiantes",
        "docentes",
        "cursos",
        "calificaciones",
        "asistencia",
        "avisos",
    ),
    Rol.DOCENTE: ("cursos", "calificaciones", "asistencia", "avisos"),
    Rol.APODERADO: ("calificaciones", "asistencia", "avisos"),
    Rol.ESTUDIANTE: ("calificaciones", "asistencia", "avisos", "calendario"),
}


def permisos_de(rol: Rol) -> tuple[str, ...]:
    """Módulos a los que puede acceder un rol (RF-S12)."""
    return _PERMISOS_POR_ROL[rol]
