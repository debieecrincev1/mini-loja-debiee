"""Cadastros com parâmetros SQL e transações para manter os dados consistentes."""

import sqlite3
from collections import Counter
from datetime import date


def cadastrar_produto(
    conexao: sqlite3.Connection,
    nome: str,
    categoria: str,
    preco_centavos: int,
    estoque: int,
) -> int:
    nome, categoria = nome.strip(), categoria.strip()
    if not nome or not categoria:
        raise ValueError("Nome e categoria são obrigatórios.")
    if type(preco_centavos) is not int or not 0 < preco_centavos <= 100_000_000:
        raise ValueError("Informe um preço positivo de até R$ 1.000.000,00.")
    if type(estoque) is not int or not 0 <= estoque <= 1_000_000:
        raise ValueError("O estoque deve ser um inteiro entre 0 e 1.000.000.")
    with conexao:
        cursor = conexao.execute(
            "INSERT INTO produtos (nome, categoria, preco_centavos, estoque) "
            "VALUES (?, ?, ?, ?)",
            (nome, categoria, preco_centavos, estoque),
        )
    return int(cursor.lastrowid)


def registrar_pedido(
    conexao: sqlite3.Connection,
    cliente_id: int,
    itens: list[tuple[int, int]],
    data_pedido: str | None = None,
) -> int:
    """Confirma um pedido inteiro ou desfaz tudo, incluindo baixas no estoque.

    itens contém pares (produto_id, quantidade). IDs repetidos são somados antes
    da validação, impedindo contornar o estoque com linhas duplicadas.
    """
    if type(cliente_id) is not int or cliente_id <= 0:
        raise ValueError("Cliente inválido.")
    if not itens:
        raise ValueError("O pedido precisa ter pelo menos um item.")
    data_texto = data_pedido if data_pedido is not None else date.today().isoformat()
    try:
        data_validada = date.fromisoformat(data_texto)
    except (TypeError, ValueError) as erro:
        raise ValueError("Data inválida; use AAAA-MM-DD.") from erro
    if data_validada.isoformat() != data_texto:
        raise ValueError("Data inválida; use AAAA-MM-DD.")

    quantidades: Counter[int] = Counter()
    for produto_id, quantidade in itens:
        if type(produto_id) is not int or produto_id <= 0:
            raise ValueError("Produto inválido.")
        if type(quantidade) is not int or not 0 < quantidade <= 1_000_000:
            raise ValueError("A quantidade deve ser um inteiro positivo até 1.000.000.")
        quantidades[produto_id] += quantidade

    with conexao:
        if not conexao.execute(
            "SELECT 1 FROM clientes WHERE id = ?", (cliente_id,)
        ).fetchone():
            raise ValueError("Cliente não encontrado.")
        cursor = conexao.execute(
            "INSERT INTO pedidos (cliente_id, data_pedido, status) "
            "VALUES (?, ?, 'concluido')", (cliente_id, data_texto),
        )
        pedido_id = int(cursor.lastrowid)
        for produto_id, quantidade in quantidades.items():
            produto = conexao.execute(
                "SELECT nome, preco_centavos FROM produtos WHERE id = ?",
                (produto_id,),
            ).fetchone()
            if produto is None:
                raise ValueError(f"Produto {produto_id} não encontrado.")
            atualizado = conexao.execute(
                "UPDATE produtos SET estoque = estoque - ? "
                "WHERE id = ? AND estoque >= ?",
                (quantidade, produto_id, quantidade),
            )
            if atualizado.rowcount != 1:
                raise ValueError(f"Estoque insuficiente: {produto['nome']}.")
            conexao.execute(
                "INSERT INTO itens_pedido "
                "(pedido_id, produto_id, quantidade, preco_unitario_centavos) "
                "VALUES (?, ?, ?, ?)",
                (pedido_id, produto_id, quantidade, produto["preco_centavos"]),
            )
    return pedido_id
