# Validação da versão entregue

Data: 28/10/2026.

Ambiente: Python 3.12.14, SQLite do módulo padrão sqlite3, Linux.

## Resultado dos testes

Comando executado na raiz do projeto:

```bash
python3 -m unittest discover -s tests -v
```

Resultado: **31 testes aprovados, sem falhas**.

| Área | Testes | O que foi conferido |
| --- | ---: | --- |
| Banco | 5 | Estrutura, amostra, integridade, relações e preservação dos dados |
| Relatórios | 8 | Totais independentes, meses, clientes, histórico e ausência de vendas |
| Cadastros | 8 | Estoque, rollback, itens repetidos, validação e SQL parametrizado |
| CSV | 3 | Acentos, valores, preservação de arquivo existente e texto de fórmulas |
| Formatação | 2 | Conversão monetária exata e rejeição de entradas ambíguas |
| Terminal | 5 | Comandos, menu, cadastro completo, caminhos com espaços e fim de entrada |
| **Total** | **31** | **Todos aprovados** |

O fluxo completo de terminal cadastra uma borracha de R$ 2,50, vende duas
unidades e confere o faturamento de R$ 450,60 e estoque final 8.

## Evidências da amostra

- `PRAGMA integrity_check`: `ok`.
- Quatro tabelas, oito clientes e oito produtos.
- Doze pedidos e 21 linhas de itens.
- Faturamento concluído: R$ 445,60.
- Ticket médio: R$ 55,70.
- Faturamento mensal: R$ 111,00, R$ 68,10 e R$ 266,50.
- Clientes sem compras concluídas: Diego, Gabriela e Hugo.

## Limites desta validação

O iniciador Windows `iniciar.bat` foi preparado para Python 3.10 ou superior,
mas não foi executado em Windows neste ambiente. Os testes de integração
executaram os mesmos módulos Python em Linux, inclusive em caminhos com espaços.

O código, os testes e o histórico Git foram verificados. A publicação está em
https://github.com/debieecrincev1/mini-loja-debiee e o Pull Request de implementação
está em https://github.com/debieecrincev1/mini-loja-debiee/pull/1 .

Os arquivos enviados inicialmente ao GitHub tiveram seus objetos Git
conferidos contra a versão local testada, incluindo o PDF. Esta atualização
modifica somente a documentação para registrar a publicação. O recebimento
do link pela plataforma do curso depende da etapa final de envio.
