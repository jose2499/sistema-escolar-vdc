import pytest

from escolar.domain.notas import parsear_nota


def test_acepta_enteros_y_decimales():
    assert parsear_nota("15") == 15.0
    assert parsear_nota("14.5") == 14.5


def test_acepta_coma_decimal_y_espacios():
    assert parsear_nota(" 14,5 ") == 14.5


def test_texto_no_numerico_da_mensaje_claro():
    with pytest.raises(ValueError, match="debe ser un número"):
        parsear_nota("abc")


def test_vacio_da_mensaje_claro():
    with pytest.raises(ValueError, match="Debes ingresar una nota"):
        parsear_nota("   ")