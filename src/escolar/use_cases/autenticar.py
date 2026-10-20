from dataclasses import dataclass

from escolar.domain.entities import Usuario
from escolar.domain.errors import CredencialesInvalidas, UsuarioInactivo
from escolar.domain.permisos import permisos_de
from escolar.domain.seguridad import formato_valido, verificar_password

_MENSAJE_GENERICO = "Credenciales inválidas"


@dataclass(frozen=True)
class Sesion:
    usuario: Usuario
    permisos: tuple[str, ...]


class AutenticarUsuario:
    def __init__(self, usuarios):
        self._usuarios = usuarios

    def ejecutar(self, dni: str, password: str) -> Sesion:
        if not formato_valido(dni, password):
            raise CredencialesInvalidas(_MENSAJE_GENERICO)
        usuario = self._usuarios.obtener_por_dni(dni)
        if usuario is None or not verificar_password(password, usuario.password_hash):
            raise CredencialesInvalidas(_MENSAJE_GENERICO)
        if not usuario.activo:
            raise UsuarioInactivo("El usuario está inactivo")
        return Sesion(usuario, permisos_de(usuario.rol))
