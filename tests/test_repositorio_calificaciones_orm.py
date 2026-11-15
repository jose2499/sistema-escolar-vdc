from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from escolar.domain.entities import Calificacion
from escolar.infrastructure.models import Base, EstudianteModel
from escolar.infrastructure.repositorios_sqlalchemy import RepositorioCalificacionesSQLAlchemy

NOTA = Calificacion("E1", "C1", 1, 15.0, "U2")


def _sembrar_estudiante(session):
    session.add(EstudianteModel(codigo="E1", nombre="Luis Quispe", dni="90000001"))
    session.commit()


def test_guardar_y_recuperar_calificacion(db_session):
    _sembrar_estudiante(db_session)
    repo = RepositorioCalificacionesSQLAlchemy(db_session)

    repo.guardar(NOTA)

    assert repo.obtener("E1", "C1", 1) == NOTA


def test_guardar_la_misma_clave_actualiza_sin_duplicar(db_session):
    _sembrar_estudiante(db_session)
    repo = RepositorioCalificacionesSQLAlchemy(db_session)

    repo.guardar(NOTA)
    repo.guardar(Calificacion("E1", "C1", 1, 18.0, "U2"))

    assert len(repo.listar()) == 1
    assert repo.obtener("E1", "C1", 1).nota == 18.0


def test_los_datos_persisten_al_reiniciar(tmp_path):
    url = f"sqlite:///{tmp_path / 'escolar_prueba.db'}"
    engine = create_engine(url)
    Base.metadata.create_all(bind=engine)

    sesion_1 = sessionmaker(bind=engine)()
    _sembrar_estudiante(sesion_1)
    RepositorioCalificacionesSQLAlchemy(sesion_1).guardar(NOTA)
    sesion_1.close()
    engine.dispose()

    # "Reinicio": un motor y una sesión nuevos sobre el mismo archivo
    engine_2 = create_engine(url)
    sesion_2 = sessionmaker(bind=engine_2)()
    assert RepositorioCalificacionesSQLAlchemy(sesion_2).obtener("E1", "C1", 1) == NOTA
    sesion_2.close()
    engine_2.dispose()
