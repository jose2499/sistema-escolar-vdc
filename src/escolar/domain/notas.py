def parsear_nota(texto):
    texto = texto.strip()
    if not texto:
        raise ValueError("Debes ingresar una nota.")
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        raise ValueError("La nota debe ser un número, por ejemplo 15 o 14.5.") from None
