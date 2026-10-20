from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class Rol(StrEnum):
    ADMIN = "admin"
    DOCENTE = "docente"
    APODERADO = "apoderado"
    ESTUDIANTE = "estudiante"


@dataclass(frozen=True)
class Usuario:
    id: str
    dni: str
    nombre: str
    rol: Rol
    password_hash: str
    activo: bool = True


@dataclass(frozen=True)
class Estudiante:
    id: str
    nombre: str
    grado: str
    seccion: str
    apoderado_id: str
    usuario_id: str | None = None


@dataclass(frozen=True)
class Curso:
    id: str
    nombre: str
    docente_id: str


@dataclass(frozen=True)
class Calificacion:
    estudiante_id: str
    curso_id: str
    periodo: int
    nota: float
    docente_id: str


class EstadoAsistencia(StrEnum):
    PRESENTE = "presente"
    FALTA = "falta"
    TARDANZA = "tardanza"
    JUSTIFICADA = "justificada"


@dataclass(frozen=True)
class Asistencia:
    estudiante_id: str
    fecha: date
    estado: EstadoAsistencia
