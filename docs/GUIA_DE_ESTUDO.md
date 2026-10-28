# Entenda o projeto sem decorar código

## 1. O que ele faz?

Uma papelaria precisa entender suas vendas. O programa lê dados de clientes,
produtos e pedidos, calcula indicadores e mostra relatórios. Também permite
cadastrar um produto e registrar uma venda com baixa de estoque.

## 2. Por que quatro tabelas?

- `clientes`: quem compra.
- `produtos`: o que a loja vende, preço atual e estoque disponível.
- `pedidos`: quem comprou, a data e o status.
- `itens_pedido`: quais produtos e quantidades pertencem a cada pedido.

Separar o pedido de seus itens permite incluir vários produtos em uma mesma
compra sem repetir os dados do cliente a cada produto.

Uma chave primária identifica um registro. Uma chave estrangeira aponta para
um registro de outra tabela e impede, por exemplo, um pedido para um cliente
inexistente. A aplicação ativa `PRAGMA foreign_keys = ON` em toda conexão.

## 3. O que os comandos SQL fazem?

| Comando | Neste projeto |
| --- | --- |
| SELECT | Busca os dados que aparecerão no relatório |
| JOIN | Liga pedido, cliente, itens e produtos |
| LEFT JOIN | Mantém também o cliente/produto que ainda não vendeu |
| WHERE | Filtra os pedidos com status concluído |
| GROUP BY | Agrupa vendas por cliente, produto ou mês |
| SUM | Soma faturamento e quantidades |
| COUNT(DISTINCT) | Conta pedidos/clientes sem duplicação por item |
| VIEW | Guarda uma consulta que pode ser reutilizada como fonte |
| INSERT | Insere um produto ou pedido |

Exemplo real: faturamento mensal a partir da visão de vendas concluídas:

```sql
SELECT SUBSTR(data_pedido, 1, 7) AS mes,
       SUM(subtotal_centavos) AS total_centavos
FROM vw_vendas_concluidas
GROUP BY SUBSTR(data_pedido, 1, 7)
ORDER BY mes;
```

Datas estão em `AAAA-MM-DD`. `SUBSTR(..., 1, 7)` transforma `2026-03-25` em
`2026-03`, permitindo somar por mês.

## 4. Por que o dinheiro está em centavos?

R$ 18,90 é armazenado como `1890`. Inteiros evitam pequenas diferenças que
podem surgir ao somar números decimais em ponto flutuante.

O item guarda o preço da venda. Se a agenda hoje custa R$ 39,90, uma venda
antiga a R$ 37,90 precisa continuar aparecendo a R$ 37,90.

## 5. Como conferir o faturamento?

Os oito pedidos concluídos somam:

55,30 + 55,70 + 32,70 + 35,40 + 94,70 + 63,30 + 39,80 + 68,70 = R$ 445,60.

O ticket médio é R$ 445,60 / 8 pedidos = R$ 55,70.
Pendentes e cancelados não entram nesse faturamento.

## 6. O que é uma transação?

Imagine um pedido com dois produtos. O primeiro tem estoque; o segundo não.
O programa precisa cancelar também a primeira baixa. A transação garante
que o pedido seja gravado inteiro ou desfeito inteiro.

Isso é feito por `with conexao:` em `src/servicos.py`. Uma exceção provoca
rollback; sem erro, o SQLite confirma as alterações.

## 7. O que vale demonstrar?

1. Abrir `iniciar.bat` ou executar `py -3 -m src.main`.
2. Escolher 1: mostrar R$ 445,60 e 8 pedidos concluídos na amostra inicial.
3. Escolher 4: mostrar faturamento por mês.
4. Escolher 3: explicar a agenda com maior receita e a régua sem vendas.
5. Escolher 7 e depois 4: exportar o relatório mensal.
6. Escolher 8: cadastrar uma borracha de R$ 2,50 com estoque 10.
7. Escolher 9: cliente 1, produto 9, quantidade 2, e ID em branco para concluir.
8. Escolher 1: o faturamento passa para R$ 450,60.

Essa sequência pressupõe um banco novo e nenhum produto cadastrado antes.
Para ensaiar sem alterar o banco principal, use `--banco data/ensaio.db`.

## 8. Como explicar os testes?

Os testes montam bancos temporários e verificam se os resultados são corretos.
Um deles força falta de estoque no segundo item para verificar se o primeiro
item e o pedido também são desfeitos. Outro confere os valores dos relatórios
com totais calculados independentemente das consultas.

## 9. O que são commit, branch e Pull Request?

- Commit: registro de uma etapa do trabalho, com mensagem e alterações.
- Branch: linha de trabalho separada da versão principal.
- Pull Request: pedido de revisão e integração dessa branch no GitHub.

O pacote tem commits e branch locais reais. Um Pull Request só existe depois
de criado no GitHub; o ZIP por si só não atende essa etapa da entrega.

## 10. Próximas melhorias possíveis

Cadastro de clientes, alteração de status com regras de estoque, filtros por
período e interface gráfica podem ser evoluções futuras. O escopo atual é
uma aplicação didática local; ele não calcula impostos, frete ou lucro.

Este material explica o que o programa faz. Use a demonstração para conferir
se consegue relacionar cada resultado com o código que o produz.
