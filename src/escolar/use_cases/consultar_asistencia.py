from dataclasses import dataclass

from escolar.domain.entities import EstadoAsistencia
from escolar.domain.errors import EntidadNoEncontrada


@dataclass(frozen=True)
class ResumenAsistencia:
    total_dias: int
    faltas: int
    porcentaje_inasistencia: float
    alerta: bool


class ConsultarAsistencia:
    def __init__(self, estudiantes, asistencias):
        self._estudiantes = estudiantes
        self._asistencias = asistencias

    def resumen(self, estudiante_id: str) -> ResumenAsistencia:
        if self._estudiantes.obtener(estudiante_id) is None:
            raise EntidadNoEncontrada(f"El estudiante {estudiante_id} no existe")
        registros = self._asistencias.listar_por_estudiante(estudiante_id)
        total = len(registros)
        faltas = len([r for r in registros if r.estado == EstadoAsistencia.FALTA])
        porcentaje = round(faltas * 100 / total, 2) if total else 0.0
        return ResumenAsistencia(total, faltas, porcentaje, faltas > 6)
