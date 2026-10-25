# src/escolar/infrastructure/models.py

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(8), unique=True, nullable=False)
    rol = Column(String(20), nullable=False)
    # Roles: admin, docente, apoderado


class Calificacion(Base):
    __tablename__ = "calificaciones"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("usuarios.id"))
    curso_id = Column(Integer, nullable=False)
    nota = Column(Float, nullable=False)
    # La nota debe estar entre 0 y 20
    bimestre = Column(Integer, nullable=False)


class Asistencia(Base):
    __tablename__ = "asistencias"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha = Column(String(10), nullable=False)
    # Formato: YYYY-MM-DD
    estado = Column(String(20), nullable=False)
    # Estados: presente, falta, tardanza
