class ErrorDeDominio(Exception):
    """Base de los errores por incumplimiento de reglas de negocio."""


class CredencialesInvalidas(ErrorDeDominio):
    """DNI o clave incorrectos o con formato inválido."""


class UsuarioInactivo(ErrorDeDominio):
    """El usuario fue dado de baja lógica y no puede ingresar."""
