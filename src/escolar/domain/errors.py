class ErrorDeDominio(Exception):
    """Base de los errores por incumplimiento de reglas de negocio."""


class CredencialesInvalidas(ErrorDeDominio):
    """DNI o clave incorrectos o con formato inválido."""


class UsuarioInactivo(ErrorDeDominio):
    """El usuario fue dado de baja lógica y no puede ingresar."""


class NotaFueraDeRango(ErrorDeDominio):
    """La nota no es un número entre 0 y 20 (CU6)."""


class PeriodoInvalido(ErrorDeDominio):
    """El período debe ser un bimestre del 1 al 4."""


class PermisoDenegado(ErrorDeDominio):
    """El usuario no tiene permiso para realizar la operación."""


class EntidadNoEncontrada(ErrorDeDominio):
    """El estudiante o curso indicado no existe."""
