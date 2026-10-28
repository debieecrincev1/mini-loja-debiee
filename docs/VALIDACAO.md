# Validação

Revisão de 28/10/2026, com Python 3.12.14 e SQLite no Linux.

```bash
python3 -m unittest discover -s tests -v
```

A suíte tem 31 testes:

| Área | Testes |
| --- | ---: |
| Banco e integridade | 5 |
| Relatórios | 8 |
| Cadastros e estoque | 8 |
| Exportação CSV | 3 |
| Formatação | 2 |
| Terminal | 5 |

Os testes cobrem preservação dos cadastros ao reabrir o banco, chaves
estrangeiras, totais de vendas, ausência de vendas, preços históricos,
estoque insuficiente, rollback do pedido e produtos repetidos. Também
conferem o CSV, os acentos e o fluxo completo pelo terminal.

Na revisão, foi reproduzida uma falha ao executar os testes com
`PYTHONIOENCODING=cp1252`: o processo filho escrevia nessa codificação,
enquanto o teste esperava UTF-8. A configuração dos processos de teste foi
ajustada para usar UTF-8 explicitamente. O iniciador Windows também
define essa codificação e mantém o código de saída da aplicação.

## Conferência dos valores

Oito pedidos concluídos somam R$ 445,60. O ticket médio é R$ 55,70. Os
meses de janeiro, fevereiro e março somam R$ 111,00, R$ 68,10 e R$ 266,50.
Pedidos pendentes e cancelados não entram nesses totais.

O teste de cadastro adiciona uma borracha de R$ 2,50, vende duas unidades e
confere faturamento de R$ 450,60 e estoque final 8. Os bancos usados nos
testes são temporários.

## Execução no GitHub

O workflow `.github/workflows/testes.yml` verifica Python 3.10 e 3.12 em
Linux e Windows. Nos jobs Windows, também executa `iniciar.bat`. O resultado
de cada execução fica na aba **Actions** do repositório.
