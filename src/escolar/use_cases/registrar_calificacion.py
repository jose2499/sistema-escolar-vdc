from escolar.domain.entities import Calificacion, Rol, Usuario
from escolar.domain.errors import EntidadNoEncontrada, PermisoDenegado
from escolar.domain.reglas_calificacion import validar_nota, validar_periodo


class RegistrarCalificacion:
    def __init__(self, estudiantes, cursos, calificaciones):
        self._estudiantes = estudiantes
        self._cursos = cursos
        self._calificaciones = calificaciones

    def ejecutar(
        self, docente: Usuario, estudiante_id: str, curso_id: str, periodo: int, nota: float
    ) -> Calificacion:
        self._exigir_docente_del_curso(docente, curso_id)
        if self._estudiantes.obtener(estudiante_id) is None:
            raise EntidadNoEncontrada(f"El estudiante {estudiante_id} no existe")
        validar_periodo(periodo)
        validar_nota(nota)
        calificacion = Calificacion(estudiante_id, curso_id, periodo, nota, docente.id)
        self._calificaciones.guardar(calificacion)
        return calificacion

    def _exigir_docente_del_curso(self, docente: Usuario, curso_id: str) -> None:
        if docente.rol is not Rol.DOCENTE:
            raise PermisoDenegado("Solo un docente puede registrar calificaciones")
        curso = self._cursos.obtener(curso_id)
        if curso is None:
            raise EntidadNoEncontrada(f"El curso {curso_id} no existe")
        if curso.docente_id != docente.id:
            raise PermisoDenegado("El docente no dicta este curso")
