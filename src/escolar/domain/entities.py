from dataclasses import dataclass
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
