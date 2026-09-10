# 📚 Sistema de Caixa e Gerenciamento de Estoque - EBP Bahia

Sistema de automação de vendas e controle de estoque para livraria, desenvolvido em Python com arquitetura desacoplada (Client-Server): interface em **Streamlit**, API em **Azure Functions** e persistência em **Supabase**.

O projeto nasceu de um problema real observado durante meu estágio na EBP Bahia (Escola Brasileira de Psicanálise): o controle manual de vendas e estoque de livros era feito em planilhas. Esta versão pública usa **dados fictícios**, por questão de confidencialidade de clientes e da instituição.

---

## 🏗️ Arquitetura do Sistema

> **Fluxo de Dados:**
> 1. **Interface Web (Streamlit):** o usuário monta o pedido e visualiza o dashboard.
> 2. **API (Azure Functions):** recebe/fornece dados via HTTP, aplica as regras de negócio.
> 3. **Persistência (Supabase):** armazena e atualiza as tabelas de estoque e vendas.

A comunicação entre front e back é feita **exclusivamente via API** — o Streamlit nunca acessa o Supabase diretamente. Isso significa que as credenciais do banco de dados ficam só no backend, nunca expostas no frontend.

### 1. Front-end (`tela_caixa.py`)
* **Caixa Registradora:** formulário de venda com carrinho dinâmico (`st.session_state`), permitindo adicionar e remover múltiplos livros antes de finalizar a venda.
* **Dashboard de Vendas:** consome o endpoint `GET /api/ObterVendas` e exibe faturamento por título em gráfico de barras, atualizado em tempo real a cada venda registrada.

### 2. Back-end (`function_app.py`)
* **`POST /api/GerarPlanilhaVendas`:** recebe o carrinho, valida estoque disponível (rejeita com `HTTP 400` se insuficiente), registra a venda e atualiza o estoque no Supabase.
* **`GET /api/ObterVendas`:** retorna todas as vendas registradas, em JSON, para o dashboard.
* **Programação defensiva:** validação estrutural do payload recebido antes de processar.

---

## ⚠️ Limitações conhecidas

* **Condição de corrida:** a verificação de estoque e o desconto são feitos em dois passos separados. Em um cenário de alta concorrência (duas vendas simultâneas do último exemplar), ambas poderiam passar pela validação antes do desconto ser aplicado. Para uso real em produção, isso pediria uma transação atômica no banco.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.11.9
* **Front-end:** Streamlit
* **Back-end/API:** Microsoft Azure Functions
* **Banco de dados:** Supabase
* **Análise de dados:** Pandas

---

## 🚀 Deploy e Execução

### Execução Local

1. Instale as dependências no ambiente virtual:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
2. Inicie a API pela tarefa `func: host start` do VS Code.
3. Em um terminal paralelo, rode a interface:
```powershell
.\.venv\Scripts\python.exe -m streamlit run tela_caixa.py
```

As portas padrão são `7071` para a API e `8501` para o Streamlit.

### Variáveis de Ambiente

**Front-end** (`.streamlit/secrets.toml` local, ou **Secrets** no Streamlit Community Cloud):
```toml
API_URL = "http://localhost:7071/api/GerarPlanilhaVendas"
```

**Back-end** (`local.settings.json` local — nunca publicado no GitHub —, ou **Configuration > Application settings** no Azure):
```text
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-do-supabase
```

### Publicação

1. Envie o projeto para um repositório GitHub.
2. Publique `tela_caixa.py` no Streamlit Community Cloud, configurando o secret `API_URL`.
3. Publique a Azure Function a partir da raiz do projeto (`function_app.py`, `host.json`, `requirements.txt`).

### Estrutura do Supabase

* `estoque`: `titulo`, `quantidade`
* `vendas`: `titulo`, `quantidade`, `valor_unitario`, `subtotal`, `valor_frete`, `valor_total`, `data_venda`, `forma_pgto`, `comprador`

O título do livro é normalizado (maiúsculas, sem espaços nas extremidades) antes da consulta ao estoque.

---

## 📂 Sobre os arquivos de planilha no repositório

As planilhas Excel presentes no repositório (com dados fictícios) não são mais utilizadas pelo sistema — elas documentam a **versão inicial** do projeto (Python + pandas/openpyxl), anterior à migração para Supabase, e foram mantidas como registro da evolução da solução.