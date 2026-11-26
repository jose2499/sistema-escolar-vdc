import pytest
from src.escolar.use_cases.consultar_calendario import consultar_calendario_academico


def test_consultar_calendario_periodo_valido():
    datos = {"2026-I": [{"fecha": "2026-05-15", "actividad": "Examen Parcial"}]}
    resultado = consultar_calendario_academico("2026-I", datos)
    assert len(resultado) == 1


def test_consultar_calendario_periodo_vacio_lanza_error():
    with pytest.raises(ValueError, match="El periodo academico es obligatorio"):
        consultar_calendario_academico("")
