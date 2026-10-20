import importlib

import pytest

CAPAS = ["domain", "use_cases", "infrastructure", "presentation"]


@pytest.mark.parametrize("capa", CAPAS)
def test_la_capa_existe(capa):
    assert importlib.import_module(f"escolar.{capa}")


def test_el_dominio_no_depende_de_capas_externas():
    import escolar.domain as dominio

    assert dominio.__name__ == "escolar.domain"
