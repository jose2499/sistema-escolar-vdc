from dataclasses import dataclass

from escolar.domain.entities import Rol, Usuario
from escolar.domain.errors import CredencialesInvalidas, UsuarioInactivo
from escolar.domain.seguridad import verificar_password

_PERMISOS = {
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


@dataclass(frozen=True)
class Sesion:
    usuario: Usuario
    permisos: tuple[str, ...]


class AutenticarUsuario:
    def __init__(self, usuarios):
        self._usuarios = usuarios

    def ejecutar(self, dni: str, password: str) -> Sesion:
        if len(dni) != 8 or not dni.isascii() or not dni.isdigit():
            raise CredencialesInvalidas("Credenciales inválidas")
        if len(password) == 0 or len(password) > 15:
            raise CredencialesInvalidas("Credenciales inválidas")
        usuario = self._usuarios.obtener_por_dni(dni)
        if usuario is None or not verificar_password(password, usuario.password_hash):
            raise CredencialesInvalidas("Credenciales inválidas")
        if not usuario.activo:
            raise UsuarioInactivo("El usuario está inactivo")
        return Sesion(usuario, _PERMISOS[usuario.rol])
