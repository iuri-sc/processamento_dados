# Processamento Distribuído Cliente-Servidor

Projeto que simula uma arquitetura distribuída onde a **Máquina A (Cliente)** envia dados brutos para a **Máquina B (Servidor/Worker)** processar, retornando um relatório estruturado via HTTP.

```
Máquina A                          Máquina B
(Cliente)                          (Servidor)

lista.txt → cliente.py  — POST →  servidor.py
                        ← JSON ←  (processa e responde)
```

---

## Estrutura do projeto

```
projeto/
├── maquina_a/
│   ├── gerar_lista.py          # Gera o arquivo de dados simulados
│   ├── cliente.py              # Lê lista.txt e envia para o servidor
│   └── relatorio_recebido.json # Gerado automaticamente após a execução
├── maquina_b/
│   └── servidor.py             # Recebe, processa e retorna o relatório
├── requirements.txt
└── README.md
```

---

## Requisitos

- Python 3.10 ou superior
- pip

---

## Instalação

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

**2. (Opcional) Crie um ambiente virtual**
```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

---

## Como executar

**Passo 1 — Gere o arquivo de dados**
```bash
cd maquina_a
python gerar_lista.py
```
Isso cria o arquivo `lista.txt` com 1000 linhas no padrão `Prefixo_Sufixo_ID`.

**Passo 2 — Suba o servidor** (Terminal 1)
```bash
cd maquina_b
python servidor.py
```
O servidor ficará escutando em `http://localhost:5000`.

**Passo 3 — Execute o cliente** (Terminal 2)
```bash
cd maquina_a
python cliente.py
```
O cliente enviará os dados e imprimirá o relatório no terminal. Um arquivo `relatorio_recebido.json` será salvo automaticamente.

---

## O que o servidor processa

Para cada linha recebida, o servidor realiza:

- **Sanitização** — remove espaços, caracteres não-ASCII e converte para maiúsculas
- **Extração de prefixo** — ex: `Sensor_Delta_1067` → `SENSOR`
- **Extração de sufixo** — ex: `Sensor_Delta_1067` → `_DELTA`
- **Extração de ID numérico** — ex: `Sensor_Delta_1067` → `1067`

O relatório retornado inclui contagem de caracteres, distribuição de prefixos e sufixos, estatísticas dos IDs (soma, média, mínimo e máximo) e uma amostra das primeiras 5 linhas convertidas.

---

## Exemplo de resposta

```json
{
  "status": "sucesso",
  "duracao_ms": 1.4,
  "origem": "Maquina-A",
  "relatorio": {
    "resumo": {
      "totalLinhasRecebidas": 1000,
      "linhasValidas": 1000,
      "linhasVazias": 0,
      "totalCaracteres": 15544,
      "mediaCaracteresPorLinha": 15.54
    },
    "estatisticasIds": {
      "soma": 5070182,
      "media": 5070.18,
      "minimo": 23,
      "maximo": 9984
    },
    "topPrefixos": [
      { "nome": "USER",   "qtd": 177 },
      { "nome": "DATA",   "qtd": 176 },
      { "nome": "SENSOR", "qtd": 173 }
    ]
  }
}
```

---

## Testando a rota manualmente

Com o servidor rodando, você pode testar via `curl`:

```bash
curl -X POST http://localhost:5000/processar \
  -H "Content-Type: application/json" \
  -d '{"origem": "teste", "linhas": ["Sensor_Alpha_123", "User_Beta_456"]}'
```

Ou verificar se o servidor está online:
```bash
curl http://localhost:5000/health
```

---

## Dependências

| Biblioteca | Uso |
|---|---|
| `flask` | Servidor HTTP na Máquina B |
| `requests` | Requisição POST na Máquina A |