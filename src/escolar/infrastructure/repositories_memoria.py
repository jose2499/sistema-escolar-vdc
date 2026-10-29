from escolar.domain.models import Rol, Usuario


class RepositorioUsuariosEnMemoria:
    def __init__(self):
        self._usuarios = [
            Usuario("10000001", "admin123", "Administrador Principal", Rol.ADMINISTRADOR),
            Usuario("20000001", "docente123", "Juan Pérez (Docente)", Rol.DOCENTE),
            Usuario("30000001", "apo12345", "Maria Gomez (Apoderado)", Rol.APODERADO),
        ]

    def obtener_por_dni(self, dni: str):
        for u in self._usuarios:
            if u.dni == dni:
                return u
        return None
