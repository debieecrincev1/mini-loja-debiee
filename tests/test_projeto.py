"""Testes de regras de negócio, integridade, relatórios, CSV e terminal.

Execute: python -m unittest discover -s tests -v
Também são compatíveis com pytest, instalado opcionalmente.
"""

import csv
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from src.database import RAIZ, TABELAS, conectar, inicializar_banco
from src.exportacao import exportar_relatorio
from src.formatacao import formatar_centavos, ler_preco
from src.queries import RELATORIOS, executar_relatorio
from src.servicos import cadastrar_produto, registrar_pedido


class CasoComBanco(unittest.TestCase):
    def setUp(self):
        self.pasta = TemporaryDirectory(prefix="mini loja teste ")
        self.caminho = Path(self.pasta.name) / "amostra.db"
        inicializar_banco(self.caminho)
        self.conexao = conectar(self.caminho)

    def tearDown(self):
        self.conexao.close()
        self.pasta.cleanup()

    def escalar(self, sql, parametros=()):
        return self.conexao.execute(sql, parametros).fetchone()[0]

    def resumo(self):
        return dict(executar_relatorio(self.conexao, "resumo")[0])


class TestBanco(CasoComBanco):
    def test_estrutura_dados_e_integridade(self):
        tabelas = {r[0] for r in self.conexao.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )}
        self.assertEqual(tabelas, TABELAS)
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM clientes"), 8)
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM produtos"), 8)
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM pedidos"), 12)
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM itens_pedido"), 21)
        self.assertEqual(self.escalar("PRAGMA integrity_check"), "ok")
        self.assertEqual(self.conexao.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_reexecucao_preserva_cadastro_e_nao_duplica_dados(self):
        novo_id = cadastrar_produto(self.conexao, "Borracha", "Escrita", 250, 10)
        self.assertFalse(inicializar_banco(self.caminho))
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM produtos"), 9)
        self.assertEqual(self.escalar("SELECT nome FROM produtos WHERE id = ?", (novo_id,)), "Borracha")
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM pedidos"), 12)

    def test_chave_estrangeira_bloqueia_cliente_inexistente(self):
        self.assertEqual(self.escalar("PRAGMA foreign_keys"), 1)
        with self.assertRaises(sqlite3.IntegrityError), self.conexao:
            self.conexao.execute(
                "INSERT INTO pedidos (cliente_id, data_pedido) VALUES (?, ?)",
                (999, "2026-04-01"),
            )

    def test_banco_rejeita_estoque_negativo_quantidade_zero_e_status_invalido(self):
        comandos = [
            ("UPDATE produtos SET estoque = -1 WHERE id = 1", ()),
            ("UPDATE itens_pedido SET quantidade = 0 WHERE id = 1", ()),
            ("UPDATE pedidos SET status = ? WHERE id = 1", ("desconhecido",)),
        ]
        for sql, parametros in comandos:
            with self.subTest(sql=sql), self.assertRaises(sqlite3.IntegrityError), self.conexao:
                self.conexao.execute(sql, parametros)

    def test_nao_altera_outro_banco_existente(self):
        outro = Path(self.pasta.name) / "outro.db"
        with sqlite3.connect(outro) as conexao:
            conexao.execute("CREATE TABLE importante (valor TEXT)")
            conexao.execute("INSERT INTO importante VALUES ('preservar')")
        with self.assertRaisesRegex(ValueError, "outro banco"):
            inicializar_banco(outro)
        with sqlite3.connect(outro) as conexao:
            self.assertEqual(conexao.execute("SELECT valor FROM importante").fetchone()[0], "preservar")


class TestRelatorios(CasoComBanco):
    def test_resumo_confere_com_calculo_independente(self):
        # Soma manual dos 8 pedidos concluídos: 55,30 + 55,70 + 32,70 +
        # 35,40 + 94,70 + 63,30 + 39,80 + 68,70 = 445,60.
        self.assertEqual(self.resumo(), {
            "pedidos": 8, "clientes": 5, "unidades": 36,
            "faturamento_centavos": 44560, "ticket_centavos": 5570,
        })

    def test_faturamento_mensal(self):
        linhas = executar_relatorio(self.conexao, "mensal")
        self.assertEqual([(r["mes"], r["pedidos"], r["total_centavos"]) for r in linhas], [
            ("2026-01", 2, 11100), ("2026-02", 2, 6810), ("2026-03", 4, 26650),
        ])

    def test_faturamento_por_cliente_inclui_clientes_com_total_zero(self):
        valores = {r["id"]: r["total_centavos"] for r in executar_relatorio(self.conexao, "clientes")}
        self.assertEqual(valores, {1: 8800, 2: 15040, 3: 3980, 4: 0, 5: 10410, 6: 6330, 7: 0, 8: 0})

    def test_produtos_usam_preco_da_venda_e_incluem_produto_nao_vendido(self):
        produtos = {r["id"]: dict(r) for r in executar_relatorio(self.conexao, "produtos")}
        self.assertEqual(produtos[4]["total_centavos"], 11570)
        self.assertEqual(produtos[8]["total_centavos"], 0)
        self.assertEqual(produtos[8]["unidades"], 0)
        self.assertEqual(sum(r["total_centavos"] for r in produtos.values()), 44560)

    def test_alterar_preco_atual_nao_altera_historico(self):
        with self.conexao:
            self.conexao.execute("UPDATE produtos SET preco_centavos = 99999")
        self.assertEqual(self.resumo()["faturamento_centavos"], 44560)

    def test_relatorio_pedidos_exibe_todos_status(self):
        linhas = executar_relatorio(self.conexao, "pedidos")
        self.assertEqual(len(linhas), 12)
        self.assertEqual(sum(r["total_centavos"] for r in linhas if r["status"] == "cancelado"), 6480)
        self.assertEqual(sum(r["total_centavos"] for r in linhas if r["status"] == "pendente"), 7160)

    def test_sem_compras_inclui_quem_tem_apenas_pedido_pendente_ou_cancelado(self):
        self.assertEqual([r["id"] for r in executar_relatorio(self.conexao, "sem_compras")], [4, 7, 8])

    def test_sem_vendas_nao_divide_por_zero(self):
        with self.conexao:
            self.conexao.execute("DELETE FROM pedidos")
        self.assertEqual(self.resumo(), {
            "pedidos": 0, "clientes": 0, "unidades": 0,
            "faturamento_centavos": 0, "ticket_centavos": 0,
        })
        self.assertEqual(executar_relatorio(self.conexao, "mensal"), [])
        for nome in RELATORIOS:
            executar_relatorio(self.conexao, nome)


class TestCadastros(CasoComBanco):
    def test_pedido_valido_baixa_estoque_e_atualiza_faturamento(self):
        pedido_id = registrar_pedido(self.conexao, 1, [(1, 2), (2, 3)], "2026-04-01")
        self.assertEqual(self.escalar("SELECT estoque FROM produtos WHERE id = 1"), 28)
        self.assertEqual(self.escalar("SELECT estoque FROM produtos WHERE id = 2"), 97)
        self.assertEqual(self.escalar("SELECT total_centavos FROM vw_totais_pedido WHERE pedido_id = ?", (pedido_id,)), 4830)
        self.assertEqual(self.resumo()["faturamento_centavos"], 49390)

    def test_estoque_insuficiente_no_segundo_item_desfaz_todo_pedido(self):
        with self.assertRaisesRegex(ValueError, "Estoque insuficiente"):
            registrar_pedido(self.conexao, 1, [(1, 2), (2, 101)], "2026-04-01")
        self.assertEqual(self.escalar("SELECT estoque FROM produtos WHERE id = 1"), 30)
        self.assertEqual(self.escalar("SELECT estoque FROM produtos WHERE id = 2"), 100)
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM pedidos"), 12)
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM itens_pedido"), 21)

    def test_produtos_repetidos_sao_somados(self):
        pedido_id = registrar_pedido(self.conexao, 1, [(1, 2), (1, 3)], "2026-04-01")
        self.assertEqual(self.escalar("SELECT quantidade FROM itens_pedido WHERE pedido_id = ?", (pedido_id,)), 5)
        self.assertEqual(self.escalar("SELECT estoque FROM produtos WHERE id = 1"), 25)

    def test_repeticao_de_produto_nao_contorna_estoque(self):
        with self.assertRaisesRegex(ValueError, "Estoque insuficiente"):
            registrar_pedido(self.conexao, 1, [(1, 20), (1, 20)])
        self.assertEqual(self.escalar("SELECT estoque FROM produtos WHERE id = 1"), 30)
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM pedidos"), 12)

    def test_produto_inexistente_desfaz_alteracoes_anteriores(self):
        with self.assertRaisesRegex(ValueError, "não encontrado"):
            registrar_pedido(self.conexao, 1, [(1, 1), (999, 1)])
        self.assertEqual(self.escalar("SELECT estoque FROM produtos WHERE id = 1"), 30)
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM pedidos"), 12)

    def test_entradas_invalidas_de_pedido_nao_criam_registros(self):
        casos = [
            (999, [(1, 1)], "2026-04-01"),
            (1, [], "2026-04-01"),
            (1, [(1, 0)], "2026-04-01"),
            (1, [(1, -1)], "2026-04-01"),
            (1, [(1, 1.5)], "2026-04-01"),
            (1, [(1, 1)], "2026-02-30"),
            (1, [(1, 1)], "20260401"),
        ]
        for cliente, itens, data_texto in casos:
            with self.subTest(itens=itens, data=data_texto), self.assertRaises(ValueError):
                registrar_pedido(self.conexao, cliente, itens, data_texto)
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM pedidos"), 12)

    def test_produto_novo_e_sql_parametrizado(self):
        nome = "Caneta 'especial'; DROP TABLE produtos; --"
        produto_id = cadastrar_produto(self.conexao, nome, "Escrita", 450, 12)
        self.assertEqual(self.escalar("SELECT nome FROM produtos WHERE id = ?", (produto_id,)), nome)
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM produtos"), 9)

    def test_cadastro_rejeita_preco_estoque_e_nome_invalidos(self):
        casos = [("", "Escrita", 100, 1), ("P", "", 100, 1),
                 ("P", "C", 0, 1), ("P", "C", 100.5, 1),
                 ("P", "C", 100, -1), ("P", "C", 100, 1.5)]
        for argumentos in casos:
            with self.subTest(argumentos=argumentos), self.assertRaises(ValueError):
                cadastrar_produto(self.conexao, *argumentos)
        self.assertEqual(self.escalar("SELECT COUNT(*) FROM produtos"), 8)


class TestCSV(CasoComBanco):
    def test_csv_acentos_separador_e_valores(self):
        caminho = exportar_relatorio(self.conexao, "produtos", Path(self.pasta.name) / "produtos.csv")
        self.assertTrue(caminho.read_bytes().startswith(b"\xef\xbb\xbf"))
        with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
            linhas = list(csv.DictReader(arquivo, delimiter=";"))
        self.assertEqual(len(linhas), 8)
        self.assertEqual(linhas[0]["Receita (R$)"], "115,70")
        self.assertEqual(linhas[-1]["Produto"], "Régua 30 cm")

    def test_csv_nao_substitui_arquivo_existente(self):
        caminho = Path(self.pasta.name) / "preservado.csv"
        caminho.write_text("preservar", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            exportar_relatorio(self.conexao, "resumo", caminho)
        self.assertEqual(caminho.read_text(encoding="utf-8"), "preservar")

    def test_csv_neutraliza_texto_interpretavel_como_formula(self):
        cadastrar_produto(self.conexao, '=HYPERLINK("exemplo")', "Escrita", 100, 1)
        caminho = exportar_relatorio(self.conexao, "produtos", Path(self.pasta.name) / "formulas.csv")
        with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
            linhas = list(csv.DictReader(arquivo, delimiter=";"))
        valor = next(l["Produto"] for l in linhas if "HYPERLINK" in l["Produto"])
        self.assertTrue(valor.startswith("'="))


class TestFormatacao(unittest.TestCase):
    def test_conversao_monetaria_exata(self):
        for texto, esperado in [("0,01", 1), ("18,90", 1890), ("18.9", 1890),
                                ("R$ 1.234,56", 123456), ("18", 1800)]:
            with self.subTest(texto=texto):
                self.assertEqual(ler_preco(texto), esperado)
        self.assertEqual(formatar_centavos(123456), "1.234,56")

    def test_rejeita_preco_ambiguo_ou_sem_centavos_validos(self):
        for texto in ["-1", "0", "NaN", "inf", "1e3", "1,234", "1.234", "1.2,30", ""]:
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                ler_preco(texto)


class TestTerminal(unittest.TestCase):
    def setUp(self):
        self.pasta = TemporaryDirectory(prefix="terminal mini loja ")
        self.banco = Path(self.pasta.name) / "banco com espacos.db"

    def tearDown(self):
        self.pasta.cleanup()

    def executar(self, *argumentos, entrada=None):
        return subprocess.run(
            [sys.executable, "-m", "src.main", "--banco", str(self.banco), *argumentos],
            input=entrada, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
            cwd=RAIZ, timeout=15,
        )

    def test_comando_resumo_e_exportacao_em_pasta_com_espacos(self):
        destino = Path(self.pasta.name) / "resumo de vendas.csv"
        processo = self.executar("--relatorio", "resumo", "--exportar", str(destino))
        self.assertEqual(processo.returncode, 0, processo.stderr)
        self.assertIn("445,60", processo.stdout)
        self.assertTrue(destino.is_file())

    def test_menu_recupera_opcao_invalida_e_exibe_relatorio(self):
        processo = self.executar(entrada="x\n1\n0\n")
        self.assertEqual(processo.returncode, 0, processo.stderr)
        self.assertIn("Opção inválida", processo.stdout)
        self.assertIn("445,60", processo.stdout)
        self.assertIn("Até a próxima", processo.stdout)

    def test_fluxo_completo_de_cadastro_no_menu(self):
        processo = self.executar(entrada="8\nBorracha\nEscrita\n2,50\n10\n9\n1\n9\n2\n\n1\n0\n")
        self.assertEqual(processo.returncode, 0, processo.stderr)
        self.assertIn("Produto 9 cadastrado", processo.stdout)
        self.assertIn("Pedido 13 concluído", processo.stdout)
        self.assertIn("450,60", processo.stdout)
        with sqlite3.connect(self.banco) as conexao:
            self.assertEqual(conexao.execute("SELECT estoque FROM produtos WHERE id = 9").fetchone()[0], 8)

    def test_exportacao_exige_relatorio_e_nao_cria_banco(self):
        processo = self.executar("--exportar", str(Path(self.pasta.name) / "erro.csv"))
        self.assertEqual(processo.returncode, 2)
        self.assertFalse(self.banco.exists())

    def test_fim_de_entrada_encerra_sem_erro(self):
        processo = self.executar(entrada="")
        self.assertEqual(processo.returncode, 0, processo.stderr)
        self.assertIn("Aplicação encerrada", processo.stdout)


if __name__ == "__main__":
    unittest.main()
