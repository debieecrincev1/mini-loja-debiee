"""Relatórios CSV com separador brasileiro, BOM UTF-8 e proteção de fórmulas."""

import csv
from pathlib import Path
import sqlite3

from .formatacao import formatar_valor
from .queries import RELATORIOS, executar_relatorio


def exportar_relatorio(
    conexao: sqlite3.Connection, nome: str, destino: str | Path
) -> Path:
    if nome not in RELATORIOS:
        raise ValueError("Relatório desconhecido.")
    consulta = RELATORIOS[nome]
    linhas = executar_relatorio(conexao, nome)
    caminho = Path(destino).expanduser()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    # 'x' evita substituir, por engano, um arquivo que já existe.
    with caminho.open("x", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(coluna.titulo for coluna in consulta.colunas)
        for linha in linhas:
            valores = []
            for coluna in consulta.colunas:
                valor = formatar_valor(linha[coluna.chave], coluna.formato)
                if coluna.formato == "texto" and valor.lstrip().startswith(("=", "+", "-", "@")):
                    valor = "'" + valor
                valores.append(valor)
            escritor.writerow(valores)
    return caminho.resolve()
