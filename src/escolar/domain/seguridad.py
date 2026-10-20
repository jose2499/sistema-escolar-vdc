import hashlib
import hmac
import os

_ITERACIONES = 120_000
LONGITUD_DNI = 8
MAX_LONGITUD_PASSWORD = 15


def _derivar(password: str, salt: bytes, iteraciones: int) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iteraciones).hex()


def hash_password(password: str, iteraciones: int = _ITERACIONES) -> str:
    salt = os.urandom(16)
    return f"{iteraciones}${salt.hex()}${_derivar(password, salt, iteraciones)}"


def verificar_password(password: str, almacenado: str) -> bool:
    try:
        iteraciones, salt_hex, hash_hex = almacenado.split("$")
        derivado = _derivar(password, bytes.fromhex(salt_hex), int(iteraciones))
    except ValueError:
        return False
    return hmac.compare_digest(derivado, hash_hex)


def formato_valido(dni: str, password: str) -> bool:
    """CU1: DNI de 8 dígitos y clave no vacía de hasta 15 caracteres."""
    dni_ok = len(dni) == LONGITUD_DNI and dni.isascii() and dni.isdigit()
    password_ok = 0 < len(password) <= MAX_LONGITUD_PASSWORD
    return dni_ok and password_ok
