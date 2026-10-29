class ErrorAutenticacion(Exception):
    pass

class AutenticarUsuario:
    def __init__(self, repo_usuarios):
        self.repo_usuarios = repo_usuarios

    def ejecutar(self, dni: str, clave: str):
        usuario = self.repo_usuarios.obtener_por_dni(dni)
        if not usuario or usuario.clave != clave:
            raise ErrorAutenticacion("Credenciales incorrectas")
        return usuario

