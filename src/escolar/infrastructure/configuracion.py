import os

RUTA_POR_DEFECTO = "escolar.db"


def obtener_url_bd(entorno=None) -> str:
    entorno = os.environ if entorno is None else entorno
    ruta = entorno.get("RUTA_DB") or RUTA_POR_DEFECTO
    return f"sqlite:///{ruta}"