import re
import time
from collections import Counter
from datetime import datetime, timezone
from flask import Flask, request, jsonify

app = Flask(__name__)


def padronizar_linha(linha: str) -> str:
    linha = linha.strip()
    linha = re.sub(r"[^\x20-\x7E]", "", linha)  # remove chars não ascii
    return linha.upper()


# retorna tudo antes do primeiro "_"
def extrair_prefixo(linha: str) -> str:
    idx = linha.find("_")
    return linha[:idx] if idx != -1 else linha


# retorna a parte do meio
def extrair_sufixo(linha: str) -> str | None:
    partes = linha.split("_")
    return f"_{partes[1]}" if len(partes) >= 3 else None


# retorna o número após o último "_"
def extrair_numero(linha: str) -> int | None:
    partes = linha.split("_")
    try:
        return int(partes[-1])
    except ValueError:
        return None


# processa o array de linhas e retorna o relatório completo
def processar_dados(linhas: list[str]) -> dict:
    total_recebidas = len(linhas)
    linhas_padronizadas = []
    linhas_vazias = 0

    contagem_prefixos: Counter = Counter()
    contagem_sufixos: Counter = Counter()

    ids: list[int] = []

    for linha in linhas:
        if not linha.strip():
            linhas_vazias += 1
            continue

        padronizada = padronizar_linha(linha)
        linhas_padronizadas.append(padronizada)

        contagem_prefixos[extrair_prefixo(padronizada)] += 1

        sufixo = extrair_sufixo(padronizada)
        if sufixo:
            contagem_sufixos[sufixo] += 1

        numero = extrair_numero(padronizada)
        if numero is not None:
            ids.append(numero)

    total_validas = len(linhas_padronizadas)
    total_caracteres = sum(len(l) for l in linhas_padronizadas)
    media_caracteres = (
        round(total_caracteres / total_validas, 2) if total_validas else 0
    )

    # estatisticas dos ids
    estatisticas_ids = {
        "soma": sum(ids),
        "media": round(sum(ids) / len(ids), 2) if ids else 0,
        "minimo": min(ids) if ids else None,
        "maximo": max(ids) if ids else None,
    }

    # top 3 prefixos
    top_prefixos = [
        {"nome": nome, "quantidade": quantidade}
        for nome, quantidade in contagem_prefixos.most_common(3)
    ]

    return {
        "resumo": {
            "totalLinhasRecebidas": total_recebidas,
            "linhasValidas": total_validas,
            "linhasVazias": linhas_vazias,
            "totalCaracteres": total_caracteres,
            "mediaCaracteresPorLinha": media_caracteres,
        },
        "estatisticas_ids": estatisticas_ids,
        "distribuicao_prefixos": dict(contagem_prefixos),
        "distribuicao_sufixos": dict(contagem_sufixos),
        "topPrefixos": top_prefixos,
        "amostraConvertida": linhas_padronizadas[:5],
    }


# rota principal
@app.post("/processar")
def processar():
    recebido_em = datetime.now(timezone.utc).isoformat()
    print(f"\n[{recebido_em}] requisição recebida - {request.content_length} bytes")

    # valida Content-Type
    if not request.is_json:
        return jsonify({"erro": "Content-Type deve ser application/json"}), 415

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"erro": "JSON invalido no corpo da requisicao"}), 400

    if not isinstance(payload.get("linhas"), list):
        return jsonify({"erro": "o campo linhas deve ser um array de strings"})

    inicio = time.perf_counter()
    relatorio = processar_dados(payload["linhas"])
    duracao = round((time.perf_counter() - inicio) * 1000, 2)  # em ms

    print(f"Processamento concluido em {duracao}ms")
    print(f"Linhas validas: {relatorio["resumo"]["linhasValidas"]}")
    print(f"Total caracteres: {relatorio["resumo"]["totalCaracteres"]}")

    return (
        jsonify(
            {
                "status": "sucesso",
                "processadoEm": recebido_em,
                "duracao_ms": duracao,
                "origem": payload.get("origem", "desconhecida"),
                "relatorio": relatorio,
            }
        ),
        200,
    )


# rota de saúde
@app.get("/health")
def health():
    return jsonify({"status": "online"}), 200


# inicialização
if __name__ == "__main__":
    print("SERVIDOR ATIVO")
    print("Escutando em http://localhost:5000")
    print("Rota: POST /processar")
    app.run(host="0.0.0.0", port=5000, debug=False)
