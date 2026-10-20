from escolar.domain.asistencia import ResumenAsistencia, calcular_resumen
from escolar.domain.errors import EntidadNoEncontrada


class ConsultarAsistencia:
    def __init__(self, estudiantes, asistencias):
        self._estudiantes = estudiantes
        self._asistencias = asistencias

    def resumen(self, estudiante_id: str) -> ResumenAsistencia:
        if self._estudiantes.obtener(estudiante_id) is None:
            raise EntidadNoEncontrada(f"El estudiante {estudiante_id} no existe")
        return calcular_resumen(self._asistencias.listar_por_estudiante(estudiante_id))
