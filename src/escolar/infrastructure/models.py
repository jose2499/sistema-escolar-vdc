
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Clase base declarativa para todas las entidades ORM."""
    pass


class EstudianteModel(Base):
    __tablename__ = "estudiantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    dni: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)

    calificaciones: Mapped[list["CalificacionModel"]] = relationship(
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

    estudiante: Mapped["EstudianteModel"] = relationship(
        "EstudianteModel", back_populates="calificaciones"
    )


class CursoModel(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)