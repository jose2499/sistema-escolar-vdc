import pytest
from escolar.use_cases.consultar_calificaciones import ConsultarCalificaciones

from escolar.domain.errors import EntidadNoEncontrada, PermisoDenegado
from escolar.use_cases.registrar_calificacion import RegistrarCalificacion


@pytest.fixture
def consultar(repo_estudiantes, repo_cursos, repo_calificaciones):
    return ConsultarCalificaciones(repo_estudiantes, repo_cursos, repo_calificaciones)


@pytest.fixture(autouse=True)
def notas(repo_estudiantes, repo_cursos, repo_calificaciones, usuarios_base):
    """E1 (apoderado U4), E2 y E3 (apoderado U5) con notas en C1 (U2) y C2 (U3)."""
    registrar = RegistrarCalificacion(repo_estudiantes, repo_cursos, repo_calificaciones)
    for est in ("E1", "E2", "E3"):
        registrar.ejecutar(usuarios_base["docente"], est, "C1", 1, 14)
        registrar.ejecutar(usuarios_base["docente2"], est, "C2", 1, 16)


def ids(calificaciones):
    return {(c.estudiante_id, c.curso_id) for c in calificaciones}


def test_el_administrador_ve_todas_las_calificaciones(consultar, usuarios_base):
    assert len(consultar.ejecutar(usuarios_base["admin"])) == 6


def test_el_docente_solo_ve_las_notas_de_sus_cursos(consultar, usuarios_base):
    visibles = consultar.ejecutar(usuarios_base["docente"])
    assert {c.curso_id for c in visibles} == {"C1"}
    assert len(visibles) == 3


def test_el_apoderado_solo_ve_las_notas_de_su_hijo(consultar, usuarios_base):
    assert ids(consultar.ejecutar(usuarios_base["apoderado"])) == {("E1", "C1"), ("E1", "C2")}


def test_un_apoderado_con_dos_hijos_ve_las_de_ambos(consultar, usuarios_base):
    visibles = ids(consultar.ejecutar(usuarios_base["apoderado2"]))
    assert {e for e, _ in visibles} == {"E2", "E3"}


def test_el_estudiante_solo_ve_sus_propias_notas(consultar, usuarios_base):
    assert ids(consultar.ejecutar(usuarios_base["estudiante"])) == {("E3", "C1"), ("E3", "C2")}


def test_el_apoderado_no_puede_pedir_las_notas_de_otro_estudiante(consultar, usuarios_base):
    with pytest.raises(PermisoDenegado):
        consultar.de_estudiante(usuarios_base["apoderado"], "E2")


def test_el_estudiante_no_puede_pedir_las_notas_de_un_companero(consultar, usuarios_base):
    with pytest.raises(PermisoDenegado):
        consultar.de_estudiante(usuarios_base["estudiante"], "E1")


def test_el_apoderado_puede_pedir_las_notas_de_su_hijo(consultar, usuarios_base):
    assert len(consultar.de_estudiante(usuarios_base["apoderado"], "E1")) == 2


def test_el_docente_solo_obtiene_sus_cursos_al_pedir_un_estudiante(consultar, usuarios_base):
    visibles = consultar.de_estudiante(usuarios_base["docente2"], "E1")
    assert ids(visibles) == {("E1", "C2")}


def test_pedir_un_estudiante_inexistente(consultar, usuarios_base):
    with pytest.raises(EntidadNoEncontrada):
        consultar.de_estudiante(usuarios_base["admin"], "E99")
