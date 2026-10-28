"""Conexão SQLite e criação inicial, sem sobrescrever dados existentes."""

import sqlite3
from contextlib import closing
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BANCO_PADRAO = RAIZ / "data" / "loja.db"
TABELAS = {"clientes", "produtos", "pedidos", "itens_pedido"}


def conectar(caminho: str | Path = BANCO_PADRAO) -> sqlite3.Connection:
    """Abre uma conexão; quem chama deve fechá-la, de preferência com closing."""
    if str(caminho) != ":memory:":
        Path(caminho).expanduser().parent.mkdir(parents=True, exist_ok=True)
        caminho = str(Path(caminho).expanduser())
    conexao = sqlite3.connect(caminho, timeout=10)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco(caminho: str | Path = BANCO_PADRAO) -> bool:
    """Cria as quatro tabelas e a amostra apenas na primeira execução.

    Retorna True se criou o banco. Estrutura e amostra entram na mesma transação.
    Se já houver tabelas inesperadas, interrompe em vez de modificar esse banco.
    """
    with closing(conectar(caminho)) as conexao:
        existentes = {
            linha[0]
            for linha in conexao.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        if existentes:
            if existentes != TABELAS:
                raise ValueError(
                    "O arquivo já contém outro banco ou uma estrutura incompleta. "
                    "Use --banco com um arquivo novo."
                )
            visoes = {linha[0] for linha in conexao.execute(
                "SELECT name FROM sqlite_master WHERE type = 'view'"
            )}
            if not {"vw_vendas_concluidas", "vw_totais_pedido"} <= visoes:
                raise ValueError("As visões do banco estão ausentes. Use um banco novo.")
            return False

        schema = (RAIZ / "sql" / "schema.sql").read_text(encoding="utf-8")
        dados = (RAIZ / "sql" / "seed.sql").read_text(encoding="utf-8")
        try:
            conexao.executescript("BEGIN IMMEDIATE;\n" + schema + dados + "\nCOMMIT;")
        except sqlite3.Error:
            conexao.rollback()
            raise
        return True
