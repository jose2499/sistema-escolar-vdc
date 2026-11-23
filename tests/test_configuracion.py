from escolar.infrastructure.configuracion import obtener_url_bd


def test_url_por_defecto_usa_escolar_db():
    assert obtener_url_bd({}) == "sqlite:///escolar.db"


def test_url_usa_la_variable_ruta_db():
    assert obtener_url_bd({"RUTA_DB": "/app/data/escolar.db"}) == "sqlite:////app/data/escolar.db"


def test_ruta_db_vacia_usa_la_ruta_por_defecto():
    assert obtener_url_bd({"RUTA_DB": ""}) == "sqlite:///escolar.db"