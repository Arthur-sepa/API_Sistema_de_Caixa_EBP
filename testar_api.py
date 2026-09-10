import urllib.request
import json

# O endereço API
url = "http://localhost:7071/api/GerarPlanilhaVendas"

# O "pacote" simulando as respostas no sistema antigo
venda_teste = {
    "comprador": "Arthur",
    "forma_pgto": "PIX",
    "carrinho_livros": [
        {
            "Titulo": "A comida e o inconsciente", 
            "Quantidade": 1,
            "Valor_Unitario": 105.00
        },
        {
            "Titulo": "Abismos",
            "Quantidade": 2,
            "Valor_Unitario": 20.00
        }
    ]
}

# Empacotando e enviando para a Nuvem (API)
print("Enviando venda para a API...")
dados_json = json.dumps(venda_teste).encode('utf-8')
requisicao = urllib.request.Request(url, data=dados_json, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(requisicao) as resposta:
        print("\n--- RESPOSTA DA API ---")
        print(f"Status: {resposta.status} (Sucesso!)")
        print(f"Mensagem: {resposta.read().decode('utf-8')}")
except Exception as erro:
    print("\n[!] Ops, deu erro na comunicação:")
    print(erro)