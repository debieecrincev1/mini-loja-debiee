"""Conversão de reais para centavos e apresentação brasileira."""

from datetime import date
from decimal import Decimal
import re


def ler_preco(texto: str) -> int:
    """Aceita 18,90, 18.90 ou 1.234,56, sem arredondar centavos ocultos."""
    texto = texto.strip().removeprefix("R$").strip()
    if "," in texto and "." in texto:
        valido = re.fullmatch(r"\d{1,3}(?:\.\d{3})+,\d{1,2}", texto)
        normalizado = texto.replace(".", "").replace(",", ".")
    else:
        valido = re.fullmatch(r"\d+(?:[,.]\d{1,2})?", texto)
        normalizado = texto.replace(",", ".")
    if not valido:
        raise ValueError("Preço inválido. Use, por exemplo, 18,90.")
    centavos = int(Decimal(normalizado) * 100)
    if not 0 < centavos <= 100_000_000:
        raise ValueError("Informe um preço positivo de até R$ 1.000.000,00.")
    return centavos


def formatar_centavos(centavos: int) -> str:
    sinal = "-" if centavos < 0 else ""
    reais, fracao = divmod(abs(int(centavos)), 100)
    inteiro = f"{reais:,}".replace(",", ".")
    return f"{sinal}{inteiro},{fracao:02d}"


def formatar_valor(valor: object, formato: str) -> str:
    if valor is None:
        return ""
    if formato == "dinheiro":
        return formatar_centavos(int(valor))
    if formato == "data":
        return date.fromisoformat(str(valor)).strftime("%d/%m/%Y")
    # Remover controles impede que nomes alterem a estrutura do terminal/CSV.
    return "".join(caractere if caractere.isprintable() else " " for caractere in str(valor))
