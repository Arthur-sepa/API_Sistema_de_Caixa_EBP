# 📚 Sistema de Caixa e Gerenciamento de Estoque - EBP Bahia

Uma solução completa de automação desenvolvida em Python para digitalizar e otimizar o fluxo de vendas e controle de catálogo de uma instituição educacional (EBP - Seção Bahia).

O sistema moderniza o controle de vendas e estoque, introduzindo uma arquitetura desacoplada (Client-Server), com persistência dos dados no Supabase e visualização por meio do Streamlit.

---

## 🏗️ Arquitetura do Sistema

O projeto foi desenhado separando a camada de interface (Front-end) da camada de lógica de negócios e manipulação de arquivos (Back-end/API).

> **Fluxo de Dados:**
> 1. **Interface Web (Streamlit):** Onde o usuário interage e monta o pedido.
> 2. **API (Azure Functions):** Recebe o pacote de dados (JSON) via HTTP POST.
> 3. **Processamento (Supabase):** A API valida as regras, atualiza o estoque e registra as vendas nas tabelas do banco de dados.

> ⚠️ **Privacidade e Proteção de Dados:** As credenciais do Supabase não devem ser publicadas no GitHub. Em produção, configure `SUPABASE_URL` e `SUPABASE_KEY` nas configurações da Azure Function.

### 1. Front-end (Interface e Dashboard)
Desenvolvido com **Streamlit**, atua como o ponto de interação do usuário final.
* **Memória de Estado (`st.session_state`):** Implementação de um carrinho de compras dinâmico, permitindo a adição de múltiplos títulos em uma única transação antes do envio para a API.
* **Correção do carrinho:** Cada item possui uma lixeira para removê-lo antes do registro da venda.
* **Dashboard Analítico:** Um painel de desempenho integrado que consome a base de Vendas e gera gráficos em tempo real utilizando **Pandas**.

### 2. Back-end (API de Processamento)
Desenvolvido com **Azure Functions**, opera de forma silenciosa processando as requisições.
* **Programação Defensiva:** Validação estrutural do payload (JSON) recebido para evitar quebras por falta de dados.
* **Regras de Negócio (Trava de Segurança):** Antes de qualquer escrita, a API realiza a leitura dinâmica do estoque. Se a quantidade solicitada for maior que a disponível, a requisição é abortada com erro `HTTP 400 (Bad Request)`, protegendo a base contra estoque negativo.
* **Persistência:** Consulta e atualização das tabelas `estoque` e `vendas` no Supabase.
* **Endpoint HTTP:** `POST /api/GerarPlanilhaVendas`.

---

## 🧹 Engenharia de Dados: O "Trator Financeiro"

Para garantir a precisão do Dashboard, foi desenvolvido um pipeline de higienização de dados na camada de visualização, lidando ativamente com anomalias comuns em inputs manuais:
* Padronização de strings (remoção de espaços invisíveis e *case normalization* para agrupamento correto).
* Tratamento de campos monetários mistos (conversão forçada de formatos textuais como `R$ 140,00` ou `1.500,00` para *float* compreensível pelo Python).
* Filtragem inteligente de valores não-contábeis na coluna de faturamento (isolamento de "Doação" ou "Consignados").

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem Principal:** Python 3.11.9
* **Front-end & Visualização:** Streamlit
* **Back-end/API:** Microsoft Azure Functions
* **Análise de Dados:** Pandas
* **Banco de dados:** Supabase

---

## 🚀 Deploy e Execução

O sistema opera com instâncias separadas para o Front-end e Back-end. 

### Execução Local
1. Instale as dependências no ambiente virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

2. Inicie a API pela tarefa `func: host start` do VS Code. Ela usa a pasta `.python_packages` para que o worker encontre o pacote `supabase`.
3. Em um terminal paralelo, rode a interface:

```powershell
.\.venv\Scripts\python.exe -m streamlit run tela_caixa.py
```

As portas padrão são `7071` para a API e `8501` para o Streamlit. Mantenha apenas uma instância de cada serviço rodando.

### Variáveis de Ambiente
Tanto em execução local quanto em nuvem, a comunicação entre o Streamlit e a Azure Function depende de `API_URL`.

No arquivo local `.streamlit/secrets.toml`:

```toml
API_URL = "http://localhost:7071/api/GerarPlanilhaVendas"
```

No Streamlit Community Cloud, use a URL HTTPS da Function em **App settings > Secrets**:

```toml
API_URL = "https://sua-function.azurewebsites.net/api/GerarPlanilhaVendas"
```

Na Azure Function, configure em **Configuration > Application settings**:

```text
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-do-supabase
```

O arquivo `local.settings.json` é apenas para desenvolvimento local e não deve ser publicado no GitHub.

### Publicação

O front-end e o back-end são publicados separadamente:

1. Envie o projeto para um repositório GitHub.
2. Publique `tela_caixa.py` no Streamlit Community Cloud.
3. Publique a Azure Function a partir da raiz do projeto, mantendo `function_app.py`, `host.json` e `requirements.txt` no mesmo nível.
4. Cadastre a URL pública da Function no segredo `API_URL` do Streamlit.


### Estrutura do Supabase

A API espera as seguintes tabelas:

* `estoque`: colunas `titulo` e `quantidade`.
* `vendas`: colunas `titulo`, `quantidade`, `valor_unitario`, `subtotal`, `valor_frete`, `valor_total`, `data_venda`, `forma_pgto` e `comprador`.

O título do livro é normalizado para letras maiúsculas e espaços nas extremidades são removidos antes da consulta ao estoque.