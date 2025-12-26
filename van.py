#!/usr/bin/env python3
import os
import subprocess
import random
import time
import json
from datetime import datetime

# =========================================================
# CONFIGURAÇÕES (AJUSTE AQUI)
# =========================================================
MASTER_HOST = "192.168.0.2"     # ex: 192.168.0.10 ou IP público
MASTER_USER = "btc"                 # usuário no master
MASTER_DIR  = "/mnt/g/PUZZLEBTC/cluster/results"

VANITY_PATH = "/root/VanitySearch/vanitysearch"
INPUT_FILE  = "71.txt"

GPU_IDS = "0,1,2,3,4,5,6,7,8,9"
THREADS = "256"
TIMEOUT = "150s"

CHECKPOINT_FILE = "checkpoint.json"
HASHRATE_LOG = "hashrate.log"

# Variáveis vindas do MASTER
WORKER_ID = os.environ.get("WORKER_ID", "0")
BASE_INI  = os.environ.get("BASE_INI")
BASE_FIM  = os.environ.get("BASE_FIM")
PCT_START = float(os.environ.get("PCT_START"))
PCT_END   = float(os.environ.get("PCT_END"))

# =========================================================
# UTILIDADES
# =========================================================
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def salvar_checkpoint(data):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f, indent=2)

def carregar_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"done": []}

# =========================================================
# RANGE BASE POR PORCENTAGEM
# =========================================================
def gerar_range_inicial(porcentagem, base_ini, base_fim):
    ini = int(base_ini, 16)
    fim = int(base_fim, 16)
    pos = ini + int((porcentagem / 100.0) * (fim - ini))
    return hex(pos)[2:].zfill(len(base_ini))

def gerar_porcentagens(inicio, fim, n):
    if n <= 1:
        return [inicio]
    inc = (fim - inicio) / (n - 1)
    return [inicio + i * inc for i in range(n)]

def gerar_ranges(pcts, base_ini, base_fim):
    out = []
    for p in pcts:
        base = gerar_range_inicial(p, base_ini, base_fim)
        ri = base[:7] + "00000000000"
        rf = base[:7] + "fffffffffff"
        out.append((p, ri, rf))
    return out

# =========================================================
# FILTROS FORTES
# =========================================================
HEX = "0123456789abcdef"

def tem_caractere_repetido(s, rep=3):
    for i in range(len(s) - rep + 1):
        if len(set(s[i:i+rep])) == 1:
            return True
    return False

def tem_sequencia_linear(s, tam=3):
    for i in range(len(s) - tam + 1):
        idx = [HEX.find(c) for c in s[i:i+tam]]
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
    base = ri[:7].lower()
    if tem_caractere_repetido(base): return False
    if tem_sequencia_linear(base): return False
    if tem_padrao_alternado(base): return False
    if tem_palavra_hex(base): return False
    return True

def filtrar_ranges(ranges, limite=500):
    filtrados = [r for r in ranges if range_valido(r[1])]
    if not filtrados:
        log("Filtro forte demais, usando fallback")
        return ranges[:limite]
    return filtrados[:limite]

# =========================================================
# MONITOR DE HASHRATE (SIMPLES)
# =========================================================
def log_hashrate():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader"],
            text=True
        )
        with open(HASHRATE_LOG, "a") as f:
            f.write(f"{datetime.now().isoformat()} | {out}")
    except Exception:
        pass

# =========================================================
# EXECUÇÃO DO VANITYSEARCH + SYNC
# =========================================================
def executar_ranges(ranges):
    ck = carregar_checkpoint()

    for p, ri, rf in ranges:
        key = f"{ri}:{rf}"
        if key in ck["done"]:
            continue

        log(f"Worker {WORKER_ID} -> {ri}:{rf}")

        cmd = [
            "timeout", TIMEOUT,
            VANITY_PATH,
            "-stop",
            "-t", THREADS,
            "-gpu",
            "-gpuId", GPU_IDS,
            "-o", f"FIDER_worker_{WORKER_ID}.txt",
            "-i", INPUT_FILE,
            "-r", f"{ri}:{rf}"
        ]

        proc = subprocess.Popen(cmd)
        start = time.time()

        while proc.poll() is None:
            log_hashrate()
            time.sleep(10)

        elapsed = int(time.time() - start)
        log(f"Finalizado em {elapsed}s")

        ck["done"].append(key)
        salvar_checkpoint(ck)

        # SYNC PARA O MASTER
        subprocess.run([
            "rsync", "-av",
            f"FIDER_worker_{WORKER_ID}.txt",
            f"{MASTER_USER}@{MASTER_HOST}:{MASTER_DIR}/"
        ])

# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    if not all([BASE_INI, BASE_FIM]):
        raise SystemExit("Variáveis BASE_INI / BASE_FIM não definidas")

    log(f"Worker {WORKER_ID} iniciado")
    log(f"PCT {PCT_START} -> {PCT_END}")

    pcts = gerar_porcentagens(PCT_START, PCT_END, 200000)
    ranges = gerar_ranges(pcts, BASE_INI, BASE_FIM)
    ranges = filtrar_ranges(ranges, limite=500)

    log(f"Ranges válidos: {len(ranges)}")
    executar_ranges(ranges)
