import pytest
from escolar.domain.entities import Rol
from escolar.domain.errors import CredencialesInvalidas, UsuarioInactivo
from escolar.use_cases.autenticar import AutenticarUsuario

PASSWORD = "clave123"


@pytest.fixture
def autenticar(repo_usuarios):
    return AutenticarUsuario(repo_usuarios)


def test_login_correcto_devuelve_la_sesion_del_usuario(autenticar, usuarios_base):
    sesion = autenticar.ejecutar("22222222", PASSWORD)
    assert sesion.usuario == usuarios_base["docente"]


def test_el_docente_tiene_calificaciones_pero_no_usuarios(autenticar):
    sesion = autenticar.ejecutar("22222222", PASSWORD)
    assert "calificaciones" in sesion.permisos
    assert "usuarios" not in sesion.permisos


def test_el_administrador_tiene_acceso_al_modulo_usuarios(autenticar):
    sesion = autenticar.ejecutar("11111111", PASSWORD)
    assert sesion.usuario.rol is Rol.ADMIN
    assert "usuarios" in sesion.permisos


def test_el_apoderado_no_puede_registrar_ni_gestionar(autenticar):
    sesion = autenticar.ejecutar("33333333", PASSWORD)
    assert set(sesion.permisos) == {"calificaciones", "asistencia", "avisos"}


def test_dni_inexistente_es_credencial_invalida(autenticar):
    with pytest.raises(CredencialesInvalidas):
        autenticar.ejecutar("99999999", PASSWORD)


def test_clave_incorrecta_es_credencial_invalida(autenticar):
    with pytest.raises(CredencialesInvalidas):
        autenticar.ejecutar("22222222", "equivocada")


@pytest.mark.parametrize("dni", ["123", "1234567890", "abcdefgh", "", "1111111a"])
def test_dni_con_formato_invalido_se_rechaza(autenticar, dni):
    with pytest.raises(CredencialesInvalidas):
        autenticar.ejecutar(dni, PASSWORD)


@pytest.mark.parametrize("clave", ["", "x" * 16])
def test_clave_vacia_o_de_mas_de_15_caracteres_se_rechaza(autenticar, clave):
    with pytest.raises(CredencialesInvalidas):
        autenticar.ejecutar("22222222", clave)


def test_usuario_inactivo_no_puede_ingresar(autenticar):
    with pytest.raises(UsuarioInactivo):
        autenticar.ejecutar("44444444", PASSWORD)


def test_usuario_inactivo_con_clave_incorrecta_no_revela_su_estado(autenticar):
    with pytest.raises(CredencialesInvalidas):
        autenticar.ejecutar("44444444", "equivocada")
