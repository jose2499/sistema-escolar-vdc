import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from src.escolar.use_cases.consultar_calendario import consultar_calendario_academico

scenarios("features/consultar_calendario.feature")


@pytest.fixture
def contexto():
    return {"fechas": {}}


@given(parsers.parse('que el estudiante "{estudiante}" ingresa al sistema'))
def estudiante_ingresa(contexto, estudiante):
    contexto["estudiante"] = estudiante


@given(parsers.parse('existen fechas programadas para el periodo "{periodo}"'))
def existen_fechas(contexto, periodo):
    datos_prueba = {
        "2026-I": [
            {"fecha": "2026-05-15", "actividad": "Examen Parcial"},
            {"fecha": "2026-07-10", "actividad": "Examen Final"},
        ],
        "2026-II": [
            {"fecha": "2026-10-20", "actividad": "Feria de Ciencias"},
        ],
    }
    contexto["fechas"][periodo] = datos_prueba.get(periodo, [])


@when(parsers.parse('consulta el calendario academico del periodo "{periodo}"'))
def consultar_periodo_valido(contexto, periodo):
    try:
        contexto["resultado"] = consultar_calendario_academico(
            periodo=periodo,
            calendario_bd=contexto["fechas"],
        )
    except ValueError as error:
        contexto["error"] = str(error)


@when('consulta el calendario academico del periodo ""')
def consultar_periodo_vacio(contexto):
    try:
        contexto["resultado"] = consultar_calendario_academico(
            periodo="",
            calendario_bd=contexto["fechas"],
        )
    except ValueError as error:
        contexto["error"] = str(error)


@then(parsers.parse("el sistema muestra {cantidad:d} actividades programadas"))
def verificar_cantidad(contexto, cantidad):
    assert len(contexto["resultado"]) == cantidad


@then(parsers.parse('el sistema rechaza la consulta con el mensaje "{mensaje}"'))
def verificar_rechazo(contexto, mensaje):
    assert contexto.get("error") == mensaje
