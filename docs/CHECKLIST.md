# Requisitos do desafio

Conferência com o [enunciado do professor](https://github.com/ckoliveiraa/Desafio-Final-Trilha-Engenharia-Dados-JR).

| Requisito | Onde conferir |
| --- | --- |
| Quatro tabelas relacionadas, com chaves primárias e estrangeiras | `sql/schema.sql` |
| Pelo menos cinco clientes e cinco produtos | `sql/seed.sql`: oito de cada |
| JOIN, WHERE, GROUP BY e funções de agregação | `sql/schema.sql` e `src/queries.py` |
| VIEW ou agregação mais elaborada | `vw_vendas_concluidas` e `vw_totais_pedido` |
| Conexão pelo módulo sqlite3 | `src/database.py` |
| Código em funções, dividido em arquivos | `src/` |
| Menu no terminal | `src/main.py` |
| Tratamento de erros | `src/main.py` e `src/database.py` |
| Instruções de execução | `README.md` e `COMECAR_AQUI.pdf` |
| requirements.txt e .gitignore | Raiz do repositório |
| Pelo menos três commits | Histórico do repositório |
| Branch de trabalho e Pull Request | `feature/mini-loja` e [PR #1 integrado](https://github.com/debieecrincev1/mini-loja-debiee/pull/1) |
| Repositório público | [mini-loja-debiee](https://github.com/debieecrincev1/mini-loja-debiee) |

Os extras implementados são exportação CSV, cadastro de produtos e pedidos,
controle de estoque e testes automatizados. A suíte usa `unittest` e também
pode ser executada por `pytest`.

Para usar um ambiente virtual no Windows:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m src.main
```

No Linux ou macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m src.main
```

O enunciado também exige as trilhas SQL e Python/Git/IA concluídas e ao
menos dois meses de pós-graduação. A etapa final é enviar o link do
repositório na plataforma, conforme [orientações de entrega](GITHUB_E_ENTREGA.md).
