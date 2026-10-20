class RepositorioUsuariosMemoria:
    def __init__(self, usuarios=()):
        self._por_dni = {u.dni: u for u in usuarios}

    def agregar(self, usuario):
        self._por_dni[usuario.dni] = usuario

    def obtener_por_dni(self, dni):
        return self._por_dni.get(dni)
