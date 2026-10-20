from collections.abc import Callable
from datetime import date

from escolar.domain.entities import Asistencia, EstadoAsistencia, Rol, Usuario
from escolar.domain.errors import (
    AsistenciaYaRegistrada,
    EntidadNoEncontrada,
    FechaInvalida,
    PermisoDenegado,
)


class RegistrarAsistencia:
    def __init__(self, estudiantes, asistencias, hoy: Callable[[], date] = date.today):
        self._estudiantes = estudiantes
        self._asistencias = asistencias
        self._hoy = hoy

    def ejecutar(
        self, docente: Usuario, estudiante_id: str, fecha: date, estado: EstadoAsistencia
    ) -> Asistencia:
        if docente.rol is not Rol.DOCENTE:
            raise PermisoDenegado("Solo un docente puede registrar asistencia")
        if self._estudiantes.obtener(estudiante_id) is None:
            raise EntidadNoEncontrada(f"El estudiante {estudiante_id} no existe")
        if fecha > self._hoy():
            raise FechaInvalida("No se puede registrar asistencia de una fecha futura")
        if self._asistencias.existe(estudiante_id, fecha):
            raise AsistenciaYaRegistrada("La asistencia de ese día ya fue registrada")
        asistencia = Asistencia(estudiante_id, fecha, estado)
        self._asistencias.guardar(asistencia)
        return asistencia
