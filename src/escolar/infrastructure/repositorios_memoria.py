class RepositorioUsuariosMemoria:
    def __init__(self, usuarios=()):
        self._por_dni = {u.dni: u for u in usuarios}

    def agregar(self, usuario):
        self._por_dni[usuario.dni] = usuario

    def obtener_por_dni(self, dni):
        return self._por_dni.get(dni)


class RepositorioEstudiantesMemoria:
    def __init__(self, estudiantes=()):
        self._por_id = {e.id: e for e in estudiantes}

    def obtener(self, estudiante_id):
        return self._por_id.get(estudiante_id)

    def listar_por_apoderado(self, apoderado_id):
        return [e for e in self._por_id.values() if e.apoderado_id == apoderado_id]

    def obtener_por_usuario(self, usuario_id):
        return next((e for e in self._por_id.values() if e.usuario_id == usuario_id), None)


class RepositorioCursosMemoria:
    def __init__(self, cursos=()):
        self._por_id = {c.id: c for c in cursos}

    def obtener(self, curso_id):
        return self._por_id.get(curso_id)

    def listar_por_docente(self, docente_id):
        return [c for c in self._por_id.values() if c.docente_id == docente_id]


class RepositorioCalificacionesMemoria:
    def __init__(self):
        self._por_clave = {}

    def guardar(self, calificacion):
        clave = (calificacion.estudiante_id, calificacion.curso_id, calificacion.periodo)
        self._por_clave[clave] = calificacion

    def obtener(self, estudiante_id, curso_id, periodo):
        return self._por_clave.get((estudiante_id, curso_id, periodo))

    def listar(self):
        return list(self._por_clave.values())


class RepositorioAsistenciaMemoria:
    def __init__(self):
        self._por_clave = {}

    def existe(self, estudiante_id, fecha):
        return (estudiante_id, fecha) in self._por_clave

    def guardar(self, asistencia):
        self._por_clave[(asistencia.estudiante_id, asistencia.fecha)] = asistencia

    def listar_por_estudiante(self, estudiante_id):
        return [a for (eid, _), a in self._por_clave.items() if eid == estudiante_id]
