from sqlalchemy import select

from escolar.domain.entities import Calificacion
from escolar.domain.errors import EntidadNoEncontrada
from escolar.infrastructure.models import CalificacionModel, EstudianteModel


class RepositorioCalificacionesSQLAlchemy:
    def __init__(self, session):
        self._session = session

    def _modelo(self, estudiante_id, curso_id, periodo):
        return self._session.scalar(
            select(CalificacionModel)
            .join(EstudianteModel)
            .where(
                EstudianteModel.codigo == estudiante_id,
                CalificacionModel.curso_id == curso_id,
                CalificacionModel.bimestre == periodo,
            )
        )

    @staticmethod
    def _a_dominio(modelo):
        return Calificacion(
            modelo.estudiante.codigo,
            modelo.curso_id,
            modelo.bimestre,
            modelo.nota,
            modelo.docente_id,
        )

    def guardar(self, calificacion):
        modelo = self._modelo(
            calificacion.estudiante_id, calificacion.curso_id, calificacion.periodo
        )
        if modelo is None:
            estudiante = self._session.scalar(
                select(EstudianteModel).where(EstudianteModel.codigo == calificacion.estudiante_id)
            )
            if estudiante is None:
                raise EntidadNoEncontrada(f"El estudiante {calificacion.estudiante_id} no existe")
            modelo = CalificacionModel(
                estudiante=estudiante,
                curso_id=calificacion.curso_id,
                bimestre=calificacion.periodo,
                nota=calificacion.nota,
                docente_id=calificacion.docente_id,
            )
            self._session.add(modelo)
        else:
            modelo.nota = calificacion.nota
            modelo.docente_id = calificacion.docente_id
        self._session.commit()

    def obtener(self, estudiante_id, curso_id, periodo):
        modelo = self._modelo(estudiante_id, curso_id, periodo)
        return self._a_dominio(modelo) if modelo else None

    def listar(self):
        return [self._a_dominio(m) for m in self._session.scalars(select(CalificacionModel))]
