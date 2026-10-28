# Conferência do enunciado

Fonte: repositório indicado na aula Desafio Engenheiro de Dados Jr:
https://github.com/ckoliveiraa/Desafio-Final-Trilha-Engenharia-Dados-JR

Este checklist separa o que está implementado do que depende da conta GitHub.

| Requisito obrigatório | Evidência | Situação |
| --- | --- | --- |
| Pelo menos 4 tabelas relacionadas com PK/FK | `sql/schema.sql`, 4 tabelas | Implementado e testado |
| Pelo menos 5 clientes e 5 produtos | `sql/seed.sql`, 8 de cada | Implementado e testado |
| JOIN, WHERE, GROUP BY e agregação | `src/queries.py` e visões SQL | Implementado e testado |
| VIEW ou agregação mais elaborada | `vw_vendas_concluidas` e `vw_totais_pedido` | Implementado e testado |
| Conexão com sqlite3 | `src/database.py` | Implementado e testado |
| Python organizado em funções | 6 módulos em `src/` | Implementado |
| Menu no terminal | `src/main.py` | Implementado e testado |
| Tratamento de erros try/except | `src/main.py`, `src/database.py` | Implementado e testado |
| README com execução | `README.md` | Concluído |
| requirements.txt e .gitignore | Raiz do projeto | Concluído |
| Pastas organizadas | `src/`, `sql/`, `data/`, `tests/`, `docs/`, `saidas/` | Concluído |
| Pelo menos 3 commits claros | Histórico Git local incluído | Concluído localmente |
| Desenvolvimento em branch de trabalho | `feature/mini-loja` | Concluído localmente |
| Pull Request para main | Precisa existir no GitHub | Pendente de publicação |
| Repositório público e link na plataforma | Precisa da conta GitHub | Pendente de publicação/entrega |

## Bônus opcionais

- Testes automatizados: 31 testes em unittest, compatíveis com pytest.
- Ambiente virtual: instruções no README; `.venv/` excluído do Git.
- Exportação CSV: disponível para os seis relatórios.
- INSERT via Python: cadastro de produtos e pedidos com controle de estoque.

## Pré-requisitos do curso

O professor pede SQL e Python/Git/IA concluídos e pelo menos dois meses na pós.
Esses requisitos de participação não são verificados pelo programa.

## Conferir antes de entregar

- [ ] Executar o programa no computador que será utilizado.
- [ ] Ler o guia de estudo e conseguir explicar banco, relatórios e transação.
- [ ] Publicar o repositório no GitHub como público.
- [ ] Abrir o Pull Request de `feature/mini-loja` para `main` e integrá-lo.
- [ ] Confirmar que README e arquivos aparecem na branch `main`.
- [ ] Abrir o link sem estar conectado e conferir o acesso público.
- [ ] Colar o link do seu repositório na atividade de entrega e verificar o recibo.
