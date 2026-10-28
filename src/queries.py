"""Consultas SQL legíveis. Faturamento considera somente pedidos concluídos."""

from dataclasses import dataclass
import sqlite3


@dataclass(frozen=True)
class Coluna:
    chave: str
    titulo: str
    formato: str = "texto"


@dataclass(frozen=True)
class Consulta:
    titulo: str
    colunas: tuple[Coluna, ...]
    sql: str


RELATORIOS = {
    "resumo": Consulta(
        "Resumo das vendas concluídas",
        (
            Coluna("pedidos", "Pedidos", "inteiro"),
            Coluna("clientes", "Clientes", "inteiro"),
            Coluna("unidades", "Unidades", "inteiro"),
            Coluna("faturamento_centavos", "Faturamento (R$)", "dinheiro"),
            Coluna("ticket_centavos", "Ticket médio (R$)", "dinheiro"),
        ),
        """
        SELECT COUNT(DISTINCT pedido_id) AS pedidos,
               COUNT(DISTINCT cliente_id) AS clientes,
               COALESCE(SUM(quantidade), 0) AS unidades,
               COALESCE(SUM(subtotal_centavos), 0) AS faturamento_centavos,
               COALESCE(CAST(ROUND(
                   SUM(subtotal_centavos) * 1.0 /
                   NULLIF(COUNT(DISTINCT pedido_id), 0)
               ) AS INTEGER), 0) AS ticket_centavos
        FROM vw_vendas_concluidas
        """,
    ),
    "clientes": Consulta(
        "Faturamento por cliente - inclui quem ainda não comprou",
        (
            Coluna("id", "ID", "inteiro"),
            Coluna("nome", "Cliente"),
            Coluna("pedidos", "Pedidos", "inteiro"),
            Coluna("total_centavos", "Total (R$)", "dinheiro"),
        ),
        """
        SELECT c.id, c.nome, COUNT(DISTINCT v.pedido_id) AS pedidos,
               COALESCE(SUM(v.subtotal_centavos), 0) AS total_centavos
        FROM clientes AS c
        LEFT JOIN vw_vendas_concluidas AS v ON v.cliente_id = c.id
        GROUP BY c.id, c.nome
        ORDER BY total_centavos DESC, c.nome, c.id
        """,
    ),
    "produtos": Consulta(
        "Produtos por faturamento - inclui produtos sem vendas",
        (
            Coluna("id", "ID", "inteiro"),
            Coluna("nome", "Produto"),
            Coluna("unidades", "Vendidos", "inteiro"),
            Coluna("total_centavos", "Receita (R$)", "dinheiro"),
            Coluna("estoque", "Estoque", "inteiro"),
        ),
        """
        SELECT p.id, p.nome, p.estoque,
               COALESCE(SUM(v.quantidade), 0) AS unidades,
               COALESCE(SUM(v.subtotal_centavos), 0) AS total_centavos
        FROM produtos AS p
        LEFT JOIN vw_vendas_concluidas AS v ON v.produto_id = p.id
        GROUP BY p.id, p.nome, p.estoque
        ORDER BY total_centavos DESC, unidades DESC, p.nome, p.id
        """,
    ),
    "mensal": Consulta(
        "Evolução mensal das vendas concluídas",
        (
            Coluna("mes", "Mês"),
            Coluna("pedidos", "Pedidos", "inteiro"),
            Coluna("unidades", "Unidades", "inteiro"),
            Coluna("total_centavos", "Faturamento (R$)", "dinheiro"),
        ),
        """
        SELECT SUBSTR(data_pedido, 1, 7) AS mes,
               COUNT(DISTINCT pedido_id) AS pedidos,
               SUM(quantidade) AS unidades,
               SUM(subtotal_centavos) AS total_centavos
        FROM vw_vendas_concluidas
        GROUP BY SUBSTR(data_pedido, 1, 7)
        ORDER BY mes
        """,
    ),
    "pedidos": Consulta(
        "Pedidos detalhados - todos os status",
        (
            Coluna("pedido_id", "Pedido", "inteiro"),
            Coluna("data_pedido", "Data", "data"),
            Coluna("cliente_nome", "Cliente"),
            Coluna("status", "Status"),
            Coluna("unidades", "Unidades", "inteiro"),
            Coluna("total_centavos", "Total (R$)", "dinheiro"),
        ),
        """
        SELECT pedido_id, data_pedido, cliente_nome, status, unidades, total_centavos
        FROM vw_totais_pedido
        ORDER BY data_pedido, pedido_id
        """,
    ),
    "sem_compras": Consulta(
        "Clientes sem compras concluídas - oportunidade de contato",
        (
            Coluna("id", "ID", "inteiro"),
            Coluna("nome", "Cliente"),
            Coluna("cidade", "Cidade"),
        ),
        """
        SELECT c.id, c.nome, c.cidade
        FROM clientes AS c
        WHERE NOT EXISTS (
            SELECT 1 FROM pedidos AS pe
            WHERE pe.cliente_id = c.id AND pe.status = 'concluido'
        )
        ORDER BY c.nome, c.id
        """,
    ),
}


def executar_relatorio(conexao: sqlite3.Connection, nome: str) -> list[sqlite3.Row]:
    if nome not in RELATORIOS:
        raise ValueError("Relatório desconhecido.")
    # O nome só seleciona uma consulta fixa; nunca é interpolado no SQL.
    return conexao.execute(RELATORIOS[nome].sql).fetchall()
