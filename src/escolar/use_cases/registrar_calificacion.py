from escolar.domain.entities import Calificacion, Rol
from escolar.domain.errors import (
    EntidadNoEncontrada,
    NotaFueraDeRango,
    PeriodoInvalido,
    PermisoDenegado,
)


class RegistrarCalificacion:
    def __init__(self, estudiantes, cursos, calificaciones):
        self._estudiantes = estudiantes
        self._cursos = cursos
        self._calificaciones = calificaciones

    def ejecutar(self, docente, estudiante_id, curso_id, periodo, nota):
        if docente.rol is not Rol.DOCENTE:
            raise PermisoDenegado("Solo un docente puede registrar calificaciones")
        curso = self._cursos.obtener(curso_id)
        if curso is None:
            raise EntidadNoEncontrada(f"El curso {curso_id} no existe")
        if curso.docente_id != docente.id:
            raise PermisoDenegado("El docente no dicta este curso")
        if self._estudiantes.obtener(estudiante_id) is None:
            raise EntidadNoEncontrada(f"El estudiante {estudiante_id} no existe")
        if periodo not in (1, 2, 3, 4):
            raise PeriodoInvalido("El período debe ser un bimestre del 1 al 4")
        if isinstance(nota, bool) or not isinstance(nota, (int, float)) or not 0 <= nota <= 20:
            raise NotaFueraDeRango("La nota debe estar entre 0 y 20")
        calificacion = Calificacion(estudiante_id, curso_id, periodo, nota, docente.id)
        self._calificaciones.guardar(calificacion)
        return calificacion
