import os
import subprocess
import random

# ----------------------------
# RANGE BASE POR PORCENTAGEM
# ----------------------------
def gerar_range_inicial(porcentagem, base_ini, base_fim):
    ini = int(base_ini, 16)
    fim = int(base_fim, 16)
    pos = ini + int((porcentagem / 100) * (fim - ini))
    return hex(pos)[2:].zfill(len(base_ini))

# ----------------------------
# PORCENTAGENS
# ----------------------------
def gerar_porcentagens_no_intervalo(inicio, fim, n):
    if inicio == fim:
        fim += 0.00001  # proteção
    inc = (fim - inicio) / (n - 1)
    return [inicio + i * inc for i in range(n)]

# ----------------------------
# GERAR RANGES
# ----------------------------
def gerar_ranges(pcts, base_ini, base_fim):
    out = []
    for p in pcts:
        base = gerar_range_inicial(p, base_ini, base_fim)
        ri = base[:7] + "00000000000"
        rf = base[:7] + "fffffffffff"
        out.append((p, ri, rf))
    return out

# ----------------------------
# FILTROS FORTES (SÓ NA PARTE REAL)
# ----------------------------
def tem_caractere_repetido(s, rep=2):
    for i in range(len(s) - rep + 1):
        if len(set(s[i:i+rep])) == 1:
            return True
    return False

def tem_sequencia_linear(s, tam=3):
    h = "0123456789abcdef"
    for i in range(len(s) - tam + 1):
        idx = [h.find(c) for c in s[i:i+tam]]
        if -1 in idx:
            continue
        if all(idx[j] + 1 == idx[j+1] for j in range(len(idx)-1)):
            return True
        if all(idx[j] - 1 == idx[j+1] for j in range(len(idx)-1)):
            return True
    return False

def tem_padrao_alternado(s):
    for i in range(len(s) - 3):
        a, b, c, d = s[i:i+4]
        if a == c and b == d and a != b:
            return True
    return False

def tem_palavra_hex(s):
    blacklist = ["dead","beef","cafe","babe","face","feed"]
    return any(w in s for w in blacklist)

def range_valido(ri):
    base = ri[:7].lower()  # <<< CORREÇÃO CRÍTICA

    if tem_caractere_repetido(base, 3):
        return False
    if tem_sequencia_linear(base, 3):
        return False
    if tem_padrao_alternado(base):
        return False
    if tem_palavra_hex(base):
        return False

    return True

def filtrar_ranges(ranges):
    filtrados = [r for r in ranges if range_valido(r[1])]
    if not filtrados:
        print("[!] Filtro muito forte — usando fallback")
        return ranges[:500]
    return filtrados

# ----------------------------
# vanity.sh
# ----------------------------
def criar_vanity_sh(ranges):
    with open("vanity.sh", "w") as sh:
        sh.write("#!/bin/bash\n\n")
        for _, ri, rf in ranges:
            sh.write(
                f"timeout 120s ./vanitysearch -stop -t 256 -gpu -gpuId 0,1,2,3,4,5,6,7,8,9 "
                f"-o FIDER.txt -i 71.txt "
                f"--keyspace {ri}:{rf}\n"
            )
            sh.write("sleep 1\n")

    os.chmod("vanity.sh", 0o755)
    subprocess.run(["bash", "vanity.sh"])

# ============================
# MAIN
# ============================
if __name__ == "__main__":

    base_ini = "400000000000000000"
    base_fim = "7fffffffffffffffff"

    inicio = 74.298095703125000000
    fim = 74.310302734375000000
    n = 200000

    print("[+] Gerando porcentagens...")
    pcts = gerar_porcentagens_no_intervalo(inicio, fim, n)

    print("[+] Gerando ranges...")
    ranges = gerar_ranges(pcts, base_ini, base_fim)

    print("[+] Aplicando filtro forte REAL...")
    validos = filtrar_ranges(ranges)

    print(f"[OK] Ranges válidos: {len(validos)}")

    selecionados = random.sample(validos, min(500, len(validos)))

    print("[+] Criando e executando vanity.sh")
    criar_vanity_sh(selecionados)
