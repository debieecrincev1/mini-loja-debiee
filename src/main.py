"""Ponto de entrada: execute python -m src.main na pasta do projeto."""

import argparse
from contextlib import closing
from datetime import datetime
from pathlib import Path
import sqlite3
import sys

from .database import BANCO_PADRAO, RAIZ, conectar, inicializar_banco
from .exportacao import exportar_relatorio
from .formatacao import formatar_centavos, formatar_valor, ler_preco
from .queries import RELATORIOS, executar_relatorio
from .servicos import cadastrar_produto, registrar_pedido


def mostrar_relatorio(conexao: sqlite3.Connection, nome: str) -> None:
    consulta = RELATORIOS[nome]
    linhas = executar_relatorio(conexao, nome)
    print(f"\n{consulta.titulo}\n")
    if not linhas:
        print("Nenhum registro encontrado.")
        return
    cabecalhos = [coluna.titulo for coluna in consulta.colunas]
    valores = [
        [formatar_valor(linha[col.chave], col.formato) for col in consulta.colunas]
        for linha in linhas
    ]
    larguras = [
        min(40, max(len(cabecalhos[i]), *(len(linha[i]) for linha in valores)))
        for i in range(len(cabecalhos))
    ]

    def imprimir(linha: list[str], cabecalho: bool = False) -> None:
        partes = []
        for indice, (texto, largura) in enumerate(zip(linha, larguras)):
            if len(texto) > largura:
                texto = texto[: largura - 3] + "..."
            numerico = consulta.colunas[indice].formato in {"dinheiro", "inteiro"}
            partes.append(texto.rjust(largura) if numerico and not cabecalho else texto.ljust(largura))
        print(" | ".join(partes))

    imprimir(cabecalhos, cabecalho=True)
    print("-+-".join("-" * largura for largura in larguras))
    for linha in valores:
        imprimir(linha)
    print(f"\n{len(linhas)} registro(s).")


def ler_inteiro(mensagem: str, minimo: int = 1) -> int:
    try:
        valor = int(input(mensagem).strip())
    except ValueError as erro:
        raise ValueError("Digite um número inteiro.") from erro
    if valor < minimo:
        raise ValueError(f"O valor mínimo é {minimo}.")
    return valor


def novo_produto(conexao: sqlite3.Connection) -> None:
    print("\nCadastrar produto")
    nome = input("Nome: ")
    categoria = input("Categoria: ")
    preco = ler_preco(input("Preço em reais (ex.: 18,90): "))
    estoque = ler_inteiro("Estoque inicial: ", minimo=0)
    produto_id = cadastrar_produto(conexao, nome, categoria, preco, estoque)
    print(f"Produto {produto_id} cadastrado com sucesso.")


def novo_pedido(conexao: sqlite3.Connection) -> None:
    print("\nClientes disponíveis")
    for cliente in conexao.execute("SELECT id, nome FROM clientes ORDER BY id"):
        print(f"  {cliente['id']}: {cliente['nome']}")
    cliente_id = ler_inteiro("ID do cliente: ")
    if not conexao.execute("SELECT 1 FROM clientes WHERE id = ?", (cliente_id,)).fetchone():
        raise ValueError("Cliente não encontrado.")
    print("\nProdutos disponíveis")
    for produto in conexao.execute("SELECT * FROM produtos WHERE estoque > 0 ORDER BY id"):
        print(f"  {produto['id']}: {produto['nome']} | "
              f"R$ {formatar_centavos(produto['preco_centavos'])} | estoque {produto['estoque']}")
    itens: list[tuple[int, int]] = []
    print("Adicione os itens. Deixe o ID em branco para concluir ou digite 0 para cancelar.")
    while True:
        texto = input("ID do produto: ").strip()
        if texto == "0":
            print("Cadastro cancelado; nenhum dado foi alterado.")
            return
        if not texto:
            break
        try:
            produto_id = int(texto)
        except ValueError as erro:
            raise ValueError("ID do produto inválido.") from erro
        quantidade = ler_inteiro("Quantidade: ")
        itens.append((produto_id, quantidade))
    pedido_id = registrar_pedido(conexao, cliente_id, itens)
    total = conexao.execute(
        "SELECT total_centavos FROM vw_totais_pedido WHERE pedido_id = ?", (pedido_id,)
    ).fetchone()[0]
    print(f"Pedido {pedido_id} concluído. Total: R$ {formatar_centavos(total)}.")


def menu(conexao: sqlite3.Connection) -> None:
    nomes = list(RELATORIOS)
    while True:
        print("\nMINI LOJA DEBIEE | Papelaria fictícia")
        for indice, nome in enumerate(nomes, start=1):
            print(f"{indice}. {RELATORIOS[nome].titulo}")
        print("7. Exportar relatório CSV (Excel)")
        print("8. Cadastrar produto")
        print("9. Registrar pedido")
        print("0. Sair")
        try:
            opcao = input("Escolha: ").strip()
            if opcao == "0":
                print("Até a próxima!")
                return
            if opcao in {str(i) for i in range(1, 7)}:
                mostrar_relatorio(conexao, nomes[int(opcao) - 1])
            elif opcao == "7":
                numero = ler_inteiro("Qual relatório exportar? (1 a 6): ")
                if numero > 6:
                    raise ValueError("Escolha um relatório de 1 a 6.")
                nome = nomes[numero - 1]
                destino = RAIZ / "saidas" / f"{nome}_{datetime.now():%Y%m%d_%H%M%S_%f}.csv"
                print(f"CSV salvo em: {exportar_relatorio(conexao, nome, destino)}")
            elif opcao == "8":
                novo_produto(conexao)
            elif opcao == "9":
                novo_pedido(conexao)
            else:
                print("Opção inválida. Escolha um número do menu.")
        except (ValueError, sqlite3.Error, OSError, OverflowError) as erro:
            print(f"Não foi possível concluir: {erro}")
        except (EOFError, KeyboardInterrupt):
            print("\nAplicação encerrada.")
            return


def main(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mini Loja Debiee - Python + SQLite")
    parser.add_argument("--banco", type=Path, default=BANCO_PADRAO, help="Caminho do banco SQLite")
    parser.add_argument("--relatorio", choices=RELATORIOS, help="Executa um relatório e encerra")
    parser.add_argument("--exportar", type=Path, help="Exporta o relatório para um novo arquivo CSV")
    args = parser.parse_args(argumentos)
    if args.exportar and not args.relatorio:
        parser.error("--exportar exige --relatorio.")
    try:
        criado = inicializar_banco(args.banco)
        if criado:
            print("Banco criado com dados fictícios de exemplo.")
        with closing(conectar(args.banco)) as conexao:
            if args.relatorio:
                mostrar_relatorio(conexao, args.relatorio)
                if args.exportar:
                    destino = exportar_relatorio(conexao, args.relatorio, args.exportar)
                    print(f"CSV salvo em: {destino}")
            else:
                print(f"Banco de dados: {args.banco.resolve()}")
                print("Faturamento inclui apenas pedidos concluídos.")
                menu(conexao)
    except (ValueError, sqlite3.Error, OSError, OverflowError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nAplicação encerrada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
