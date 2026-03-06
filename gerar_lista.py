""" """

import random

TOTAL_LINHAS = 1000
PREFIXOS = ["User", "Data", "Sensor", "Node", "System", "Admin"]
SUFIXOS = ["_Alpha", "_Beta", "_Gamma", "Delta", "_Omega", "_Final"]
ARQUIVO = "lista.txt"

linhas = []

for _ in range(TOTAL_LINHAS):
    prefixo = random.choice(PREFIXOS)
    sufixo = random.choice(SUFIXOS)
    id_num = random.randint(0, 9999)
    linhas.append(f"{prefixo}{sufixo}_{id_num}")

with open(ARQUIVO, "w", encoding="utf-8") as f:
    f.write("\n".join(linhas) + "\n")

print(f"Arquivo {ARQUIVO} com {TOTAL_LINHAS} linhas gerado com sucesso!")
