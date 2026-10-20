from datetime import date, timedelta

import pytest

from escolar.domain.entities import EstadoAsistencia
from escolar.domain.errors import EntidadNoEncontrada
from escolar.use_cases.consultar_asistencia import ConsultarAsistencia
from escolar.use_cases.registrar_asistencia import RegistrarAsistencia

INICIO = date(2026, 3, 2)


@pytest.fixture
def consultar(repo_estudiantes, repo_asistencia):
    return ConsultarAsistencia(repo_estudiantes, repo_asistencia)


@pytest.fixture
def cargar(repo_estudiantes, repo_asistencia, usuarios_base, reloj):
    registrar = RegistrarAsistencia(repo_estudiantes, repo_asistencia, hoy=reloj)

    def _cargar(estudiante_id, estados):
        for i, estado in enumerate(estados):
            registrar.ejecutar(
                usuarios_base["docente"], estudiante_id, INICIO + timedelta(i), estado
            )

    return _cargar


F, P = EstadoAsistencia.FALTA, EstadoAsistencia.PRESENTE


def test_sin_registros_el_porcentaje_es_cero_y_no_hay_alerta(consultar):
    resumen = consultar.resumen("E1")
    assert (resumen.total_dias, resumen.faltas, resumen.porcentaje_inasistencia) == (0, 0, 0.0)
    assert resumen.alerta is False


def test_calcula_el_porcentaje_de_inasistencia(consultar, cargar):
    cargar("E1", [F, F, P, P, P, P, P, P])
    resumen = consultar.resumen("E1")
    assert resumen.total_dias == 8
    assert resumen.faltas == 2
    assert resumen.porcentaje_inasistencia == 25.0


def test_el_porcentaje_se_redondea_a_dos_decimales(consultar, cargar):
    cargar("E1", [F, P, P])
    assert consultar.resumen("E1").porcentaje_inasistencia == 33.33


def test_con_6_faltas_todavia_no_hay_alerta(consultar, cargar):
    cargar("E1", [F] * 6 + [P] * 4)
    assert consultar.resumen("E1").alerta is False


def test_con_7_faltas_se_excede_el_limite_y_hay_alerta(consultar, cargar):
    cargar("E1", [F] * 7 + [P] * 3)
    assert consultar.resumen("E1").alerta is True


def test_tardanzas_y_justificadas_no_cuentan_como_falta(consultar, cargar):
    estados = [EstadoAsistencia.TARDANZA] * 5 + [EstadoAsistencia.JUSTIFICADA] * 5
    cargar("E1", estados)
    resumen = consultar.resumen("E1")
    assert resumen.faltas == 0
    assert resumen.alerta is False


def test_las_faltas_de_un_estudiante_no_afectan_a_otro(consultar, cargar):
    cargar("E1", [F] * 8)
    assert consultar.resumen("E2").faltas == 0


def test_estudiante_inexistente(consultar):
    with pytest.raises(EntidadNoEncontrada):
        consultar.resumen("E99")
