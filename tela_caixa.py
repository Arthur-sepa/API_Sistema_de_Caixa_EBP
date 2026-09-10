import streamlit as st
import requests
import pandas as pd
import os

# Configuração visual da página (layout='wide' deixa a tela mais larga para caber os gráficos)
st.set_page_config(page_title="Sistema EBP Bahia", layout="wide")

# ==========================================
# MENU LATERAL
# ==========================================
st.sidebar.title("Navegação")
menu = st.sidebar.radio("Ir para:", ["🛒 Caixa Registradora", "📊 Dashboard de Vendas"])

# ==========================================
# TELA 1: O CAIXA
# ==========================================
if menu == "🛒 Caixa Registradora":
    st.title("📚 Sistema de Caixa - EBP")
    st.markdown("---")

    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    st.subheader("1. Dados do Cliente")
    comprador = st.text_input("Nome do Comprador:")
    forma_pgto = st.selectbox("Forma de Pagamento:", ["PIX", "Dinheiro", "Doação", "Cartão de Crédito", "Cartão de Débito"])

    st.markdown("---")
    st.subheader("2. Adicionar Livro")
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        titulo_livro = st.text_input("Título do Livro (exatamente como no estoque):")
    with col2:
        quantidade = st.number_input("Qtd:", min_value=1, step=1)
    with col3:
        valor_unit = st.number_input("Valor Unit (R$):", min_value=0.0, step=0.50)
    with col4:
        valor_frete = st.number_input("Frete (R$):", min_value=0.0, step=0.50)

    if st.button("➕ Adicionar ao Carrinho"):
        if titulo_livro:
            st.session_state.carrinho.append({
                "Titulo": titulo_livro,
                "Quantidade": quantidade,
                "Valor_Unitario": valor_unit,
                "Valor_Frete": valor_frete,
            })
            st.success(f"'{titulo_livro}' adicionado à comanda!")
        else:
            st.warning("⚠️ Digite o título do livro primeiro.")

    st.markdown("---")

    if len(st.session_state.carrinho) > 0:
        st.subheader("🛒 Resumo da Comanda")
        total_venda = 0
        
        for index, item in enumerate(st.session_state.carrinho):
            subtotal = item['Quantidade'] * item['Valor_Unitario']
            frete = item.get('Valor_Frete', 0.0)
            total_item = subtotal + frete
            total_venda += total_item
            
            col_texto, col_botao = st.columns([4, 1])
            
            with col_texto:
                st.write(f"- {item['Quantidade']}x **{item['Titulo']}** (livros: R$ {subtotal:.2f} + frete: R$ {frete:.2f} = R$ {total_item:.2f})")
            
            with col_botao:
                if st.button("🗑️", key=f"remover_{index}"):
                    st.session_state.carrinho.pop(index)
                    st.rerun()
        
        st.write(f"### Total Geral: R$ {total_venda:.2f}")

        if st.button("Registrar Venda Completa 🚀"):
            if not comprador:
                st.warning("⚠️ Preencha o nome do comprador lá em cima!")
            else:
                with st.spinner("Enviando para o servidor e atualizando planilhas..."):
                    pacote_venda = {
                        "comprador": comprador,
                        "forma_pgto": forma_pgto,
                        "carrinho_livros": st.session_state.carrinho
                    }
                    url_api = st.secrets.get(
                        "API_URL",
                        os.getenv("API_URL", "http://localhost:7071/api/GerarPlanilhaVendas"),
                    )
                    try:
                        resposta = requests.post(url_api, json=pacote_venda, timeout=30)
                        if resposta.status_code == 200:
                            st.success(f"✅ {resposta.text}")
                            st.session_state.carrinho = []
                        else:
                            st.error(f"❌ Erro na API: {resposta.text}")
                    except requests.RequestException as erro:
                        st.error(f"❌ Não foi possível conectar com a API: {erro}")

# ==========================================
# TELA 2: O DASHBOARD DE DADOS (SUPABASE)
# ==========================================
elif menu == "📊 Dashboard de Vendas":
    st.title("📊 Painel de Desempenho")
    st.markdown("---")
    
    try:
        from supabase import create_client
        
        supabase_url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
        supabase_key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
        
        if not supabase_url or not supabase_key:
            st.error("❌ Credenciais do Supabase não encontradas no secrets.toml!")
        else:
            supabase = create_client(supabase_url, supabase_key)
            resposta = supabase.table("vendas").select("*").execute()
            
            df = pd.DataFrame(resposta.data)
            
            if df.empty:
                st.info("📭 Nenhuma venda registrada no banco de dados ainda.")
            else:
                st.write(f"### Dados vindos direto do Supabase ({len(df)} registros encontrados)")
                
                # Exibe a tabela crua para conferência das colunas exatas do Supabase
                st.dataframe(df)
                
                # Normaliza os nomes das colunas para maiúsculo
                df.columns = df.columns.str.upper()
                
                col_titulo = "TITULO" if "TITULO" in df.columns else df.columns[1]
                col_valor = "VALOR_TOTAL" if "VALOR_TOTAL" in df.columns else df.columns[5]
                
                df[col_titulo] = df[col_titulo].astype(str).str.upper().str.strip()
                df[col_valor] = pd.to_numeric(df[col_valor], errors='coerce').fillna(0.0)
                
                faturamento = df.groupby(col_titulo)[col_valor].sum().reset_index()
                st.bar_chart(data=faturamento, x=col_titulo, y=col_valor)
                
    except Exception as e:
        st.warning(f"Erro ao carregar dados do Supabase: {e}")