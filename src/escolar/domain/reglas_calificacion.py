import math

from escolar.domain.errors import NotaFueraDeRango, PeriodoInvalido

NOTA_MINIMA = 0
NOTA_MAXIMA = 20
PERIODOS_VALIDOS = (1, 2, 3, 4)


def validar_nota(nota) -> None:
    """CU6: no se registran calificaciones menores a 0 ni mayores a 20."""
    es_numero = isinstance(nota, (int, float)) and not isinstance(nota, bool)
    if not es_numero or math.isnan(nota) or not NOTA_MINIMA <= nota <= NOTA_MAXIMA:
        raise NotaFueraDeRango(f"La nota debe estar entre {NOTA_MINIMA} y {NOTA_MAXIMA}")


def validar_periodo(periodo) -> None:
    if periodo not in PERIODOS_VALIDOS:
        raise PeriodoInvalido("El período debe ser un bimestre del 1 al 4")
