from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Clase base declarativa para todas las entidades ORM."""

    pass


class EstudianteModel(Base):
    __tablename__ = "estudiantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    dni: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    codigo: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)

    calificaciones: Mapped[list["CalificacionModel"]] = relationship(
        "CalificacionModel", back_populates="estudiante", cascade="all, delete-orphan"
    )


class CalificacionModel(Base):
    __tablename__ = "calificaciones"
    __table_args__ = (
        CheckConstraint("nota >= 0 AND nota <= 20", name="ck_calificaciones_nota_rango"),
        UniqueConstraint(
            "estudiante_id", "curso_id", "bimestre", name="uq_calificacion_est_curso_bim"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nota: Mapped[float] = mapped_column(Float, nullable=False)
    bimestre: Mapped[int] = mapped_column(Integer, nullable=False)
    estudiante_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("estudiantes.id"), nullable=False
    )
    curso_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    docente_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estudiante: Mapped["EstudianteModel"] = relationship(
        "EstudianteModel", back_populates="calificaciones"
    )


class CursoModel(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
