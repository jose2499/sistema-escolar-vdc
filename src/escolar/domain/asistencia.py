from collections.abc import Iterable
from dataclasses import dataclass

from escolar.domain.entities import Asistencia, EstadoAsistencia

LIMITE_INASISTENCIAS = 6


@dataclass(frozen=True)
class ResumenAsistencia:
    total_dias: int
    faltas: int
    porcentaje_inasistencia: float
    alerta: bool


def calcular_resumen(registros: Iterable[Asistencia]) -> ResumenAsistencia:
    """Solo las faltas injustificadas cuentan; se alerta al superar el límite (CU4)."""
    registros = list(registros)
    total = len(registros)
    faltas = sum(1 for r in registros if r.estado is EstadoAsistencia.FALTA)
    porcentaje = round(faltas * 100 / total, 2) if total else 0.0
    return ResumenAsistencia(total, faltas, porcentaje, faltas > LIMITE_INASISTENCIAS)
