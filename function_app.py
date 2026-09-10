import azure.functions as func
import logging
import datetime
import os
from supabase import create_client, Client

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="GerarPlanilhaVendas", methods=["POST"])
def GerarPlanilhaVendas(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('API acionada! Iniciando processamento do caixa no Supabase...')

    try:
        # 1. RECEBENDO O PACOTE DE DADOS
        req_body = req.get_json()
        comprador = req_body.get('comprador')
        forma_pgto = req_body.get('forma_pgto')
        carrinho_livros = req_body.get('carrinho_livros', [])
        
        if not comprador or not forma_pgto or not carrinho_livros:
            return func.HttpResponse("Faltam dados!", status_code=400)

        data_hoje = datetime.datetime.now().strftime("%d/%m/%Y")
        
        # 2. CONECTANDO AO BANCO DE DADOS SUPABASE
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(url, key)

        # 3. VERIFICANDO ESTOQUE (A TRAVA DE SEGURANÇA)
        for item in carrinho_livros:
            titulo_digitado = str(item['Titulo']).upper().strip()
            quantidade_desejada = int(item['Quantidade'])
            
            # Vai no banco e busca o livro específico
            resposta_estoque = supabase.table('estoque').select('*').eq('titulo', titulo_digitado).execute()
            
            if len(resposta_estoque.data) == 0:
                return func.HttpResponse(f"Livro não encontrado no catálogo: '{item['Titulo']}'", status_code=400)
            
            estoque_atual = resposta_estoque.data[0]['quantidade']
            
            if estoque_atual < quantidade_desejada:
                return func.HttpResponse(f"Estoque insuficiente! '{item['Titulo']}' tem apenas {estoque_atual} unidades.", status_code=400)

        # 4. REGISTRANDO A VENDA E DESCONTANDO ESTOQUE
        valor_total_compra = 0

        for item in carrinho_livros:
            titulo_digitado = str(item['Titulo']).upper().strip()
            valor_unitario = float(item['Valor_Unitario'])
            quantidade = int(item['Quantidade'])
            valor_frete = float(item.get('Valor_Frete', 0))
            subtotal = valor_unitario * quantidade
            total_item = subtotal + valor_frete
            valor_total_compra += total_item
            
            # A. Atualiza o estoque (Subtração Matemática Direta)
            # Lê novamente para garantir que pega o valor atualizado e subtrai
            estoque_banco = supabase.table('estoque').select('quantidade').eq('titulo', titulo_digitado).execute().data[0]['quantidade']
            nova_qtd = estoque_banco - quantidade
            supabase.table('estoque').update({'quantidade': nova_qtd}).eq('titulo', titulo_digitado).execute()
            
            # B. Salva a linha de Venda
            dados_venda = {
                "titulo": titulo_digitado,
                "quantidade": quantidade,
                "valor_unitario": valor_unitario,
                "subtotal": subtotal,
                "valor_frete": valor_frete,
                "valor_total": total_item,
                "data_venda": data_hoje,
                "forma_pgto": forma_pgto.upper(),
                "comprador": comprador
            }
            supabase.table('vendas').insert(dados_venda).execute()
            logging.info(f"Venda registrada e estoque atualizado: {titulo_digitado}")

        mensagem_sucesso = f"Venda de R$ {valor_total_compra:.2f} para {comprador} registrada com sucesso no banco de dados!"
        return func.HttpResponse(mensagem_sucesso, status_code=200)

    except Exception as e:
        logging.error(f"Erro no processamento: {str(e)}")
        return func.HttpResponse(f"Erro interno no servidor: {str(e)}", status_code=500)