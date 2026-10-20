from escolar.domain.entities import Estudiante, Rol, Usuario
from escolar.domain.errors import PermisoDenegado


def exigir_relacion_con_estudiante(usuario: Usuario, estudiante: Estudiante) -> None:
    """RF-S11: un apoderado solo accede a sus hijos y un estudiante solo a sí mismo."""
    if usuario.rol is Rol.APODERADO and estudiante.apoderado_id != usuario.id:
        raise PermisoDenegado("El estudiante no está asociado a este apoderado")
    if usuario.rol is Rol.ESTUDIANTE and estudiante.usuario_id != usuario.id:
        raise PermisoDenegado("Un estudiante solo puede ver sus propias notas")
