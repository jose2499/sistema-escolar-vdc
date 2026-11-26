def consultar_calendario_academico(
    periodo: str,
    calendario_bd: dict[str, list[dict[str, str]]] | None = None,
) -> list[dict[str, str]]:
    """Consulta las actividades académicas programadas para un periodo."""
    if not periodo or not periodo.strip():
        raise ValueError("El periodo academico es obligatorio")

    datos = calendario_bd or {}
    return list(datos.get(periodo.strip(), []))
