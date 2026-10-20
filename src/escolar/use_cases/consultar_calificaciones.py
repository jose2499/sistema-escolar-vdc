from collections.abc import Callable

from escolar.domain.entities import Calificacion, Rol, Usuario
from escolar.domain.errors import EntidadNoEncontrada
from escolar.domain.visibilidad import exigir_relacion_con_estudiante

Predicado = Callable[[Calificacion], bool]


class ConsultarCalificaciones:
    def __init__(self, estudiantes, cursos, calificaciones):
        self._estudiantes = estudiantes
        self._cursos = cursos
        self._calificaciones = calificaciones

    def ejecutar(self, usuario: Usuario) -> list[Calificacion]:
        es_visible = self._predicado_de_visibilidad(usuario)
        return [c for c in self._calificaciones.listar() if es_visible(c)]

    def de_estudiante(self, usuario: Usuario, estudiante_id: str) -> list[Calificacion]:
        estudiante = self._estudiantes.obtener(estudiante_id)
        if estudiante is None:
            raise EntidadNoEncontrada(f"El estudiante {estudiante_id} no existe")
        exigir_relacion_con_estudiante(usuario, estudiante)
        return [c for c in self.ejecutar(usuario) if c.estudiante_id == estudiante_id]

    def _predicado_de_visibilidad(self, usuario: Usuario) -> Predicado:
        if usuario.rol is Rol.ADMIN:
            return lambda _: True
        if usuario.rol is Rol.DOCENTE:
            cursos = {c.id for c in self._cursos.listar_por_docente(usuario.id)}
            return lambda c: c.curso_id in cursos
        if usuario.rol is Rol.APODERADO:
            hijos = {e.id for e in self._estudiantes.listar_por_apoderado(usuario.id)}
            return lambda c: c.estudiante_id in hijos
        propio = self._estudiantes.obtener_por_usuario(usuario.id)
        return lambda c: propio is not None and c.estudiante_id == propio.id
