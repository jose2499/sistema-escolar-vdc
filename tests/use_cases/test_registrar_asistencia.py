from datetime import date

import pytest
from escolar.use_cases.registrar_asistencia import RegistrarAsistencia

from escolar.domain.entities import EstadoAsistencia
from escolar.domain.errors import (
    AsistenciaYaRegistrada,
    EntidadNoEncontrada,
    FechaInvalida,
    PermisoDenegado,
)

HOY = date(2026, 10, 20)


@pytest.fixture
def registrar(repo_estudiantes, repo_asistencia, reloj):
    return RegistrarAsistencia(repo_estudiantes, repo_asistencia, hoy=reloj)


def test_el_docente_registra_la_asistencia_de_un_estudiante(
    registrar, usuarios_base, repo_asistencia
):
    asistencia = registrar.ejecutar(usuarios_base["docente"], "E1", HOY, EstadoAsistencia.PRESENTE)
    assert asistencia.estado is EstadoAsistencia.PRESENTE
    assert repo_asistencia.listar_por_estudiante("E1") == [asistencia]


@pytest.mark.parametrize("rol", ["admin", "apoderado", "estudiante"])
def test_solo_un_docente_registra_asistencia(registrar, usuarios_base, rol):
    with pytest.raises(PermisoDenegado):
        registrar.ejecutar(usuarios_base[rol], "E1", HOY, EstadoAsistencia.PRESENTE)


def test_estudiante_inexistente(registrar, usuarios_base):
    with pytest.raises(EntidadNoEncontrada):
        registrar.ejecutar(usuarios_base["docente"], "E99", HOY, EstadoAsistencia.PRESENTE)


def test_una_asistencia_ya_registrada_no_se_puede_modificar(
    registrar, usuarios_base, repo_asistencia
):
    registrar.ejecutar(usuarios_base["docente"], "E1", HOY, EstadoAsistencia.FALTA)
    with pytest.raises(AsistenciaYaRegistrada):
        registrar.ejecutar(usuarios_base["docente"], "E1", HOY, EstadoAsistencia.PRESENTE)
    assert repo_asistencia.listar_por_estudiante("E1")[0].estado is EstadoAsistencia.FALTA


def test_el_mismo_dia_se_puede_registrar_a_otro_estudiante(registrar, usuarios_base):
    registrar.ejecutar(usuarios_base["docente"], "E1", HOY, EstadoAsistencia.PRESENTE)
    registrar.ejecutar(usuarios_base["docente"], "E2", HOY, EstadoAsistencia.FALTA)


def test_no_se_registra_asistencia_de_una_fecha_futura(registrar, usuarios_base):
    with pytest.raises(FechaInvalida):
        registrar.ejecutar(
            usuarios_base["docente"], "E1", date(2026, 10, 21), EstadoAsistencia.PRESENTE
        )
