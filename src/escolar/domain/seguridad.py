import hashlib
import hmac
import os

_ITERACIONES = 120_000


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
