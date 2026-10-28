# Publicar e entregar preservando commits e Pull Request

O pacote ZIP contém a pasta `.git` com histórico local real. Extraia a pasta
inteira e mantenha `.git`. Não execute `git init` novamente.
Os commits foram criados pelo assistente e identificados assim no histórico.

## 1. Antes de publicar

Abra o terminal na pasta `mini-loja-debiee` e confira:

```bash
git status
git branch --show-current
git log --oneline
```

A branch atual deve ser `feature/mini-loja`. O código e a documentação estão
nela. A `main` guarda a base inicial do projeto, permitindo um PR com alterações.

Se o comando `git` não existir, instale o Git pelo site oficial:
https://git-scm.com/downloads .

## 2. Criar o repositório público

Na sua conta GitHub, crie um repositório chamado `mini-loja-debiee`, com
visibilidade **Public**. Crie-o vazio, sem adicionar README, licença ou
gitignore pela interface, pois esses arquivos já estão no projeto local.

Copie a URL HTTPS fornecida pelo próprio GitHub. No comando abaixo,
`URL_HTTPS_COPIADA_DO_GITHUB` é um marcador: substitua pela URL real.

```bash
git remote add origin URL_HTTPS_COPIADA_DO_GITHUB
git push -u origin main
git push -u origin feature/mini-loja
```

Se o Git pedir autenticação, conclua o acesso pelo fluxo do GitHub.
Não cole senha ou token em arquivos do projeto.

## 3. Abrir e integrar o Pull Request

No repositório, abra um Pull Request com:

- Base: `main`.
- Compare: `feature/mini-loja`.
- Título: `Implementa mini loja com Python, SQL e SQLite`.

Descrição sugerida:

> Implementa uma aplicação de terminal para uma papelaria fictícia, com quatro
> tabelas relacionadas, seis relatórios SQL e exportação CSV. Inclui cadastro
> de produtos e pedidos com controle transacional de estoque. Validação:
> 31 testes automatizados aprovados com Python 3.12.14.

Revise os arquivos e integre o PR para `main`. Se houver escolha de estratégia,
use **Create a merge commit**, preservando os commits individuais exigidos.
Depois confira que o código aparece na `main` e que o PR está marcado como
integrado (merged).

## 4. Entregar na plataforma

Copie a URL do seu repositório público. A atividade encontrada na plataforma,
em Desafio - Entrega projeto Engenheiro de Dados Junior, contém a aula
**Entrega do projeto final Engenheiro Dados Junior**, com o campo
**Cole o link da sua entrega** e o botão **Enviar link**.

Cole a URL do seu repositório, envie e confira a confirmação exibida.
O link do professor serve como referência; a entrega é o link do seu projeto.

## Se o histórico não aparecer após extrair

Verifique se a pasta `.git` está presente. Ela é uma pasta oculta em alguns
sistemas. Use `git log --oneline` para conferir antes da publicação. Se o
histórico não estiver disponível, recupere a pasta original deste pacote.
