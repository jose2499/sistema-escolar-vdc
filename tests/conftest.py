import pytest

from escolar.domain.entities import Rol, Usuario
from escolar.domain.seguridad import hash_password
from escolar.infrastructure.repositorios_memoria import RepositorioUsuariosMemoria

PASSWORD = "clave123"


@pytest.fixture
def usuarios_base():
    h = hash_password(PASSWORD, iteraciones=1000)
    return {
        "admin": Usuario("U1", "11111111", "Ana Admin", Rol.ADMIN, h),
        "docente": Usuario("U2", "22222222", "Diego Docente", Rol.DOCENTE, h),
        "docente2": Usuario("U3", "55555555", "Dora Docente", Rol.DOCENTE, h),
        "apoderado": Usuario("U4", "33333333", "Ada Apoderada", Rol.APODERADO, h),
        "apoderado2": Usuario("U5", "66666666", "Aldo Apoderado", Rol.APODERADO, h),
        "estudiante": Usuario("U6", "77777777", "Eli Estudiante", Rol.ESTUDIANTE, h),
        "inactivo": Usuario("U7", "44444444", "Ivan Inactivo", Rol.DOCENTE, h, activo=False),
    }


@pytest.fixture
def repo_usuarios(usuarios_base):
    return RepositorioUsuariosMemoria(usuarios_base.values())
