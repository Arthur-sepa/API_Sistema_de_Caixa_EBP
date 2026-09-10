# 📝 Estudos e Anotações - Streamlit e Back-end

Este documento registra os principais conceitos arquiteturais aprendidos durante o desenvolvimento do sistema de caixa.

## 1. Arquitetura Desacoplada (Client-Server)
* **Front-end (Streamlit):** Atua apenas como a interface (o "Garçom"). Coleta os dados, formata em JSON e envia o pacote.
* **Back-end (Azure Functions):** Atua como o processador (a "Cozinha"). Recebe o JSON, valida regras de negócio, atualiza o Excel (OpenPyXL) e devolve um Status HTTP.

## 2. O Motor do Streamlit
* **Re-run Top-Down:** A cada interação do usuário, o Streamlit recarrega o script da linha 1 à última.
* **Session State (`st.session_state`):** Um cofre de memória volátil. Essencial para guardar dados que precisam sobreviver ao re-run contínuo (ex: itens de um carrinho de compras).

## 3. Limpeza de Dados (Pandas)
Planilhas reais contêm dados "sujos". O Pandas exige tratamento rigoroso antes de gerar gráficos:
* Padronização de strings (`.str.upper().str.strip()`).
* Remoção de caracteres monetários indesejados e conversão de formatação (troca de `,` por `.`).
* Conversão forçada para números numéricos, isolando textos como "DOAÇÃO".

## 4. Programação Defensiva e HTTP
* O código do servidor deve prever falhas no envio dos dados. O uso de `dicionario.get('chave', valor_padrao)` evita que a API quebre se um dado faltar.
* **HTTP 200 (OK):** Operação de atualização de planilhas bem-sucedida.
* **HTTP 400 (Bad Request):** Requisição negada por regra de negócio (ex: estoque insuficiente ou livro inexistente).