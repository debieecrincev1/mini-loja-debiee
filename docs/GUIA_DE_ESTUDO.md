# Modelagem e regras

## Tabelas

`clientes` guarda nome, e-mail e cidade. `produtos` contém nome, categoria,
preço atual e estoque. `pedidos` identifica o cliente, a data e o status da
compra. `itens_pedido` registra os produtos, as quantidades e os preços
praticados em cada pedido.

Separar os itens do pedido permite registrar vários produtos na mesma
compra. A combinação de pedido e produto é única; se um produto for
informado mais de uma vez, as quantidades são somadas antes da gravação.

As chaves estrangeiras são ativadas em toda conexão com
`PRAGMA foreign_keys = ON`. Quantidades positivas, estoque não negativo e
os três status aceitos também têm restrições no banco.

## Consultas

`vw_vendas_concluidas` junta as quatro tabelas e mantém somente pedidos
concluídos. Os relatórios de faturamento usam essa visão.
`vw_totais_pedido` reúne os totais de todos os pedidos, inclusive pendentes
e cancelados, para permitir a conferência.

No faturamento por cliente e por produto, o `LEFT JOIN` mantém os registros
sem venda. No relatório de clientes sem compras, `NOT EXISTS` verifica a
ausência de pedidos concluídos.

Exemplo de agrupamento mensal:

```sql
SELECT SUBSTR(data_pedido, 1, 7) AS mes,
       SUM(subtotal_centavos) AS total_centavos
FROM vw_vendas_concluidas
GROUP BY SUBSTR(data_pedido, 1, 7)
ORDER BY mes;
```

A data usa o formato `AAAA-MM-DD`. Os sete primeiros caracteres identificam
o mês. O ticket médio divide o faturamento pelo número de pedidos distintos,
evitando contar um pedido mais de uma vez por ele ter vários itens.

## Preços e estoque

Os valores são inteiros em centavos: R$ 18,90 é armazenado como `1890`.
O preço do item é copiado no momento da venda e não acompanha alterações
posteriores no cadastro do produto.

O estoque da amostra representa o saldo disponível depois das vendas
históricas. Pedidos pendentes não reservam estoque. Novos pedidos são
registrados como concluídos e descontam o saldo disponível.

Pedido, itens e baixa de estoque são gravados em uma transação. Uma falha,
como falta de saldo no segundo item, desfaz também as alterações do primeiro.
Os valores informados pelo usuário entram nas consultas por parâmetros SQL.

## Escopo

O cadastro de pedidos usa os clientes da amostra. Cadastro de clientes,
alteração de status, frete, impostos e cálculo de lucro ficam fora desta
versão. Os relatórios mostram receita de vendas.
