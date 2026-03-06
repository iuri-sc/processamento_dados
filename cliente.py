import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import requests

# configuração
SERVIDOR_URL = "http://localhost:5000/processar"
ARQUIVO_DADOS = Path(__file__).parent / "lista.txt"
ARQUIVO_SAIDA = Path(__file__).parent / "relatorio_recebido.json"

# leitura do arquivo local
if not ARQUIVO_DADOS.exists():
    print(f"Arquivo nao encontrado: {ARQUIVO_DADOS}")
    print("Execute primeiro: py gerar_lista.py")
    sys.exit(1)
    
conteudo = ARQUIVO_DADOS.read_text(encoding="utf-8")
linhas = conteudo.splitlines()

print(f"Arquivo lido: {ARQUIVO_DADOS}")
print(f"Total de linhas: {len(linhas)}")

# montagem do payload
payload = {
    "origem": "maquina cliente",
    "enviadoEm": datetime.now(timezone.utc).isoformat(),
    "totalLinhas": len(linhas),
    "linhas": linhas
}

payload_str = json.dumps(payload, ensure_ascii=False)
tamanho_kb = len(payload_str.encode("utf-8")) / 1024

print(f"\n Payload montado")
print(f"Tamanho: {tamanho_kb:.2f} KB")

# enviar via POST
print(f"\nEnviando para {SERVIDOR_URL}...")

try: 
    resposta = requests.post(
        SERVIDOR_URL,
        json=payload, # serializa e define content-type automaticamente
        timeout=30
    )
except requests.exceptions.ConnectionError:
    print("\nErro de conexao com o servidor")
    print("verifique se o servidor está rodando: py servidor.py")
    sys.exit(1)
except requests.exceptions.Timeout:
    print("\nTimeout: o servidor demorou mais de 30s para responder")
    sys.exit(1)
    
print(f"\nResposta recebida - HTTP {resposta.status_code}")

if resposta.status_code != 200:
    print(f"Erro do servidor: {resposta.json().get("erro")}")
    sys.exit(1)
    
dados = resposta.json()
r = dados["relatorio"]

# exibicao do relatorio
print(f"Processado em: {dados["processadoEm"]}")
print(f"Duração: {dados["duracao_ms"]} ms")
print(f"Origem: {dados["origem"]}")
print("RESUMO GERAL")
print(f"Linhas recebidas: {r["resumo"]["totalLinhasRecebidas"]}")
print(f"Linhas válidas: {r["resumo"]["linhasValidas"]}")
print(f"Linhas vazias: {r["resumo"]["linhasVazias"]}")
print(f"Total caracteres: {r["resumo"]["totalCaracteres"]}")
print(f"Média chars/linha: {r["resumo"]["mediaCaracteresPorLinha"]}")
print("ESTATISTICAS DOS IDs NUMÉRICOS")
print(f"Soma: {r['estatisticas_ids']['soma']}")
print(f"Média: {r['estatisticas_ids']['media']}")
print(f"Minimo: {r['estatisticas_ids']['minimo']}")
print(f"Maximo: {r['estatisticas_ids']['maximo']}")
print("DISTRIBUIÇÃO DE PREFIXOS")
for nome, quantidade in r["distribuicao_prefixos"].items():
    print(f"{nome:<10}: {quantidade}")

print("DISTRIBUIÇÃO DE SUFIXOS")
for nome, quantidade in r["distribuicao_sufixos"].items():
    print(f"{nome:<10}: {quantidade}")
    
print("TOP 3 PREFIXOS")
for i, p in enumerate(r["topPrefixos"], start=1):
    print(f"{i}. {p["nome"]} ({p["quantidade"]} ocorrencias)")
    
print("AMOSTRA (5 primeiras linhas convertidas)")
for i, linha in enumerate(r["amostraConvertida"], start=1):
    print(f"{i}. {linha}")
    
# salva o relatorio em json
ARQUIVO_SAIDA.write_text(
    json.dumps(dados, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Relatório salvo em: {ARQUIVO_SAIDA}")