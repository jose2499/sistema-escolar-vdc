from sqlalchemy import select

from escolar.infrastructure.models import CalificacionModel, CursoModel, EstudianteModel


def test_guardar_estudiante_con_sus_calificaciones(db_session):
    # Dado un estudiante con dos calificaciones asociadas
    estudiante = EstudianteModel(nombre="Ana Quispe", dni="12345678")
    CalificacionModel(nota=18, bimestre=1, estudiante=estudiante)
    CalificacionModel(nota=15, bimestre=2, estudiante=estudiante)

    # Cuando se persiste en la base de datos
    db_session.add(estudiante)
    db_session.commit()

    # Entonces se consulta y se recupera con sus relaciones
    stmt = select(EstudianteModel).filter_by(nombre="Ana Quispe")
    estudiante_db = db_session.scalars(stmt).first()

    assert estudiante_db is not None
    assert len(estudiante_db.calificaciones) == 2
    assert estudiante_db.calificaciones[0].estudiante.nombre == "Ana Quispe"


def test_eliminar_estudiante_elimina_sus_calificaciones(db_session):
    # Dado un estudiante con una calificación persistida
    estudiante = EstudianteModel(nombre="Luis Ramos", dni="87654321")
    CalificacionModel(nota=12, bimestre=1, estudiante=estudiante)
    db_session.add(estudiante)
    db_session.commit()

    # Cuando se elimina el estudiante
    db_session.delete(estudiante)
    db_session.commit()

    # Entonces sus calificaciones también desaparecen de la base de datos
    calificacion_db = db_session.scalars(
        select(CalificacionModel).filter_by(nota=12)
    ).first()
    assert calificacion_db is None


def test_guardar_curso(db_session):
    # Dado un curso nuevo
    curso = CursoModel(nombre="Historia")
    
    # Cuando se persiste en la base de datos
    db_session.add(curso)
    db_session.commit()
    
    # Entonces se recupera de la base de datos
    curso_db = db_session.scalars(select(CursoModel).filter_by(nombre="Historia")).first()
    assert curso_db is not None