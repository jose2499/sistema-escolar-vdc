from enum import Enum

class Rol(Enum):
    ADMINISTRADOR = "administrador"
    DOCENTE = "docente"
    APODERADO = "apoderado"

class Usuario:
    def __init__(self, dni: str, clave: str, nombre_completo: str, rol: Rol):
        self.dni = dni
        self.clave = clave
        self.nombre_completo = nombre_completo
        self.rol = rol

