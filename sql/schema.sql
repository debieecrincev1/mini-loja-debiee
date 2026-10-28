-- Valores monetários são inteiros em centavos, evitando erros de ponto flutuante.
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    email TEXT NOT NULL UNIQUE,
    cidade TEXT NOT NULL
);

CREATE TABLE produtos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    categoria TEXT NOT NULL CHECK (length(trim(categoria)) > 0),
    preco_centavos INTEGER NOT NULL
        CHECK (typeof(preco_centavos) = 'integer' AND preco_centavos > 0),
    estoque INTEGER NOT NULL
        CHECK (typeof(estoque) = 'integer' AND estoque >= 0)
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    data_pedido TEXT NOT NULL CHECK (length(data_pedido) = 10),
    status TEXT NOT NULL DEFAULT 'concluido'
        CHECK (status IN ('concluido', 'pendente', 'cancelado'))
);

CREATE TABLE itens_pedido (
    id INTEGER PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    quantidade INTEGER NOT NULL
        CHECK (typeof(quantidade) = 'integer' AND quantidade > 0),
    preco_unitario_centavos INTEGER NOT NULL
        CHECK (typeof(preco_unitario_centavos) = 'integer'
               AND preco_unitario_centavos > 0),
    UNIQUE (pedido_id, produto_id)
);

CREATE INDEX idx_pedidos_cliente ON pedidos(cliente_id);
CREATE INDEX idx_pedidos_status_data ON pedidos(status, data_pedido);
CREATE INDEX idx_itens_produto ON itens_pedido(produto_id);

-- Cada linha representa um produto de um pedido efetivamente concluído.
-- O preço do item preserva o valor da venda, mesmo se o preço atual mudar.
CREATE VIEW vw_vendas_concluidas AS
SELECT pe.id AS pedido_id, pe.data_pedido,
       c.id AS cliente_id, c.nome AS cliente_nome,
       p.id AS produto_id, p.nome AS produto_nome, p.categoria,
       i.quantidade, i.preco_unitario_centavos,
       i.quantidade * i.preco_unitario_centavos AS subtotal_centavos
FROM pedidos AS pe
JOIN clientes AS c ON c.id = pe.cliente_id
JOIN itens_pedido AS i ON i.pedido_id = pe.id
JOIN produtos AS p ON p.id = i.produto_id
WHERE pe.status = 'concluido';

CREATE VIEW vw_totais_pedido AS
SELECT pe.id AS pedido_id, pe.data_pedido, pe.status,
       c.nome AS cliente_nome,
       COALESCE(SUM(i.quantidade), 0) AS unidades,
       COALESCE(SUM(i.quantidade * i.preco_unitario_centavos), 0)
           AS total_centavos
FROM pedidos AS pe
JOIN clientes AS c ON c.id = pe.cliente_id
LEFT JOIN itens_pedido AS i ON i.pedido_id = pe.id
GROUP BY pe.id, pe.data_pedido, pe.status, c.nome;
