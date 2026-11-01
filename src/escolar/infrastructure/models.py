<<<<<<< HEAD

=======
from typing import List
>>>>>>> 2516c1ed33d027b4184c4220729e6a813da47580
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
<<<<<<< HEAD
    """Clase base declarativa para todas las entidades ORM."""
=======
>>>>>>> 2516c1ed33d027b4184c4220729e6a813da47580
    pass


class EstudianteModel(Base):
    __tablename__ = "estudiantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    dni: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)

<<<<<<< HEAD
    calificaciones: Mapped[list["CalificacionModel"]] = relationship(
=======
    calificaciones: Mapped[List["CalificacionModel"]] = relationship(
>>>>>>> 2516c1ed33d027b4184c4220729e6a813da47580
        "CalificacionModel", back_populates="estudiante", cascade="all, delete-orphan"
    )


class CalificacionModel(Base):
    __tablename__ = "calificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nota: Mapped[float] = mapped_column(Float, nullable=False)
    bimestre: Mapped[int] = mapped_column(Integer, nullable=False)
    estudiante_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("estudiantes.id"), nullable=False
    )
<<<<<<< HEAD

    estudiante: Mapped["EstudianteModel"] = relationship(
        "EstudianteModel", back_populates="calificaciones"
    )


class CursoModel(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
=======

    estudiante: Mapped["EstudianteModel"] = relationship(
        "EstudianteModel", back_populates="calificaciones"
    )
>>>>>>> 2516c1ed33d027b4184c4220729e6a813da47580
