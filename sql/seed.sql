-- Dados inteiramente fictícios. O domínio .example é reservado para exemplos.
INSERT INTO clientes (id, nome, email, cidade) VALUES
    (1, 'Ana Lisboa', 'ana@papelaria.example', 'Curitiba'),
    (2, 'Bruno Andrade', 'bruno@papelaria.example', 'Londrina'),
    (3, 'Carla Mendes', 'carla@papelaria.example', 'Maringá'),
    (4, 'Diego Rocha', 'diego@papelaria.example', 'Curitiba'),
    (5, 'Elisa Fontes', 'elisa@papelaria.example', 'Ponta Grossa'),
    (6, 'Felipe Santos', 'felipe@papelaria.example', 'Londrina'),
    (7, 'Gabriela Costa', 'gabriela@papelaria.example', 'Cascavel'),
    (8, 'Hugo Freitas', 'hugo@papelaria.example', 'Curitiba');

-- Estoque representa o saldo disponível após as vendas históricas da amostra.
-- Pedidos pendentes não reservam estoque neste modelo didático.
INSERT INTO produtos (id, nome, categoria, preco_centavos, estoque) VALUES
    (1, 'Caderno universitário', 'Cadernos', 1890, 30),
    (2, 'Caneta azul', 'Escrita', 350, 100),
    (3, 'Lapiseira 0,7 mm', 'Escrita', 1290, 40),
    (4, 'Agenda planner', 'Organização', 3990, 20),
    (5, 'Marca-texto', 'Escrita', 790, 60),
    (6, 'Estojo', 'Acessórios', 2490, 25),
    (7, 'Bloco adesivo', 'Organização', 990, 50),
    (8, 'Régua 30 cm', 'Acessórios', 650, 35);

INSERT INTO pedidos (id, cliente_id, data_pedido, status) VALUES
    (1, 1, '2026-01-08', 'concluido'),
    (2, 2, '2026-01-12', 'concluido'),
    (3, 3, '2026-01-20', 'cancelado'),
    (4, 1, '2026-02-02', 'concluido'),
    (5, 4, '2026-02-10', 'pendente'),
    (6, 5, '2026-02-15', 'concluido'),
    (7, 2, '2026-03-01', 'concluido'),
    (8, 6, '2026-03-05', 'concluido'),
    (9, 3, '2026-03-12', 'concluido'),
    (10, 5, '2026-03-20', 'concluido'),
    (11, 4, '2026-03-22', 'cancelado'),
    (12, 7, '2026-03-25', 'pendente');

INSERT INTO itens_pedido
    (pedido_id, produto_id, quantidade, preco_unitario_centavos) VALUES
    (1, 1, 2, 1890), (1, 2, 5, 350),
    (2, 4, 1, 3990), (2, 5, 2, 790),
    (3, 6, 1, 2490),
    (4, 3, 1, 1290), (4, 7, 2, 990),
    (5, 1, 3, 1890),
    (6, 6, 1, 2490), (6, 2, 3, 350),
    -- Venda histórica com outro preço: o relatório usa 3790, não o preço atual.
    (7, 4, 2, 3790), (7, 1, 1, 1890),
    (8, 7, 4, 990), (8, 5, 3, 790),
    (9, 3, 2, 1290), (9, 2, 4, 350),
    (10, 1, 1, 1890), (10, 6, 2, 2490),
    (11, 4, 1, 3990),
    (12, 5, 1, 790), (12, 2, 2, 350);
