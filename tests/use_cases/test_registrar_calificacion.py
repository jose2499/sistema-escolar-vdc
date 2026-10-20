import pytest

from escolar.domain.errors import (
    EntidadNoEncontrada,
    NotaFueraDeRango,
    PeriodoInvalido,
    PermisoDenegado,
)
from escolar.use_cases.registrar_calificacion import RegistrarCalificacion


@pytest.fixture
def registrar(repo_estudiantes, repo_cursos, repo_calificaciones):
    return RegistrarCalificacion(repo_estudiantes, repo_cursos, repo_calificaciones)


def test_el_docente_del_curso_registra_una_nota_valida(
    registrar, usuarios_base, repo_calificaciones
):
    cal = registrar.ejecutar(usuarios_base["docente"], "E1", "C1", 1, 15)
    assert cal.nota == 15
    assert repo_calificaciones.obtener("E1", "C1", 1) == cal


@pytest.mark.parametrize("nota", [0, 20, 10.5, 1, 19.99])
def test_notas_dentro_del_rango_0_a_20_se_aceptan(registrar, usuarios_base, nota):
    assert registrar.ejecutar(usuarios_base["docente"], "E1", "C1", 1, nota).nota == nota


@pytest.mark.parametrize("nota", [-1, -0.01, 20.01, 21, 100, float("nan"), "15", None, True])
def test_notas_fuera_de_rango_o_no_numericas_se_rechazan(registrar, usuarios_base, nota):
    with pytest.raises(NotaFueraDeRango):
        registrar.ejecutar(usuarios_base["docente"], "E1", "C1", 1, nota)


def test_una_nota_rechazada_no_se_guarda(registrar, usuarios_base, repo_calificaciones):
    with pytest.raises(NotaFueraDeRango):
        registrar.ejecutar(usuarios_base["docente"], "E1", "C1", 1, 25)
    assert repo_calificaciones.listar() == []


def test_un_docente_ajeno_al_curso_no_puede_registrar(registrar, usuarios_base):
    with pytest.raises(PermisoDenegado):
        registrar.ejecutar(usuarios_base["docente2"], "E1", "C1", 1, 15)


@pytest.mark.parametrize("rol", ["admin", "apoderado", "estudiante"])
def test_solo_un_docente_puede_registrar_notas(registrar, usuarios_base, rol):
    with pytest.raises(PermisoDenegado):
        registrar.ejecutar(usuarios_base[rol], "E1", "C1", 1, 15)


def test_curso_inexistente(registrar, usuarios_base):
    with pytest.raises(EntidadNoEncontrada):
        registrar.ejecutar(usuarios_base["docente"], "E1", "C99", 1, 15)


def test_estudiante_inexistente(registrar, usuarios_base):
    with pytest.raises(EntidadNoEncontrada):
        registrar.ejecutar(usuarios_base["docente"], "E99", "C1", 1, 15)


@pytest.mark.parametrize("periodo", [0, 5, -1])
def test_el_periodo_debe_ser_un_bimestre_del_1_al_4(registrar, usuarios_base, periodo):
    with pytest.raises(PeriodoInvalido):
        registrar.ejecutar(usuarios_base["docente"], "E1", "C1", periodo, 15)


def test_registrar_dos_veces_la_misma_nota_actualiza_y_no_duplica(
    registrar, usuarios_base, repo_calificaciones
):
    registrar.ejecutar(usuarios_base["docente"], "E1", "C1", 1, 12)
    registrar.ejecutar(usuarios_base["docente"], "E1", "C1", 1, 14)
    assert len(repo_calificaciones.listar()) == 1
    assert repo_calificaciones.obtener("E1", "C1", 1).nota == 14
