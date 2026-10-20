from escolar.domain.entities import Rol
from escolar.domain.errors import EntidadNoEncontrada, PermisoDenegado


class ConsultarCalificaciones:
    def __init__(self, estudiantes, cursos, calificaciones):
        self._estudiantes = estudiantes
        self._cursos = cursos
        self._calificaciones = calificaciones

    def ejecutar(self, usuario):
        todas = self._calificaciones.listar()
        if usuario.rol is Rol.ADMIN:
            return todas
        elif usuario.rol is Rol.DOCENTE:
            cursos = {c.id for c in self._cursos.listar_por_docente(usuario.id)}
            return [c for c in todas if c.curso_id in cursos]
        elif usuario.rol is Rol.APODERADO:
            hijos = {e.id for e in self._estudiantes.listar_por_apoderado(usuario.id)}
            return [c for c in todas if c.estudiante_id in hijos]
        elif usuario.rol is Rol.ESTUDIANTE:
            estudiante = self._estudiantes.obtener_por_usuario(usuario.id)
            if estudiante is None:
                return []
            return [c for c in todas if c.estudiante_id == estudiante.id]
        return []

    def de_estudiante(self, usuario, estudiante_id):
        estudiante = self._estudiantes.obtener(estudiante_id)
        if estudiante is None:
            raise EntidadNoEncontrada(f"El estudiante {estudiante_id} no existe")
        if usuario.rol is Rol.APODERADO and estudiante.apoderado_id != usuario.id:
            raise PermisoDenegado("El estudiante no está asociado a este apoderado")
        if usuario.rol is Rol.ESTUDIANTE and estudiante.usuario_id != usuario.id:
            raise PermisoDenegado("Un estudiante solo puede ver sus propias notas")
        return [c for c in self.ejecutar(usuario) if c.estudiante_id == estudiante_id]
