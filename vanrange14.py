#!/usr/bin/env python3
from decimal import Decimal
from pathlib import Path
import math

# Opções de incremento
incrementos_opcoes = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 10,
    7: 100,
    8: 1000,
    9: 10000,
    10: 100000,
    11: 1000000
}

# Escolha do incremento
print("Escolha o incremento:")
for k, v in incrementos_opcoes.items():
    print(f"{k} -> incremento de {v}")
opcao = int(input("Digite a opção (1-8): ").strip())

if opcao not in incrementos_opcoes:
    raise ValueError("Opção inválida!")

incremento = incrementos_opcoes[opcao]

# Escolha de bits
bits_opcoes = {
    11: (28, 11, "0000000", "fffffff"),
    10: (32, 10, "00000000", "ffffffff"),
    9: (36, 9, "000000000", "fffffffff"),
    8: (40, 8, "0000000000", "ffffffffff"),
    7: (44, 7, "00000000000", "fffffffffff"),
    6: (48, 6, "000000000000", "ffffffffffff"),
    5: (52, 5, "0000000000000", "fffffffffffff"),
    4: (56, 4, "00000000000000", "ffffffffffffff"),
    3: (60, 3, "000000000000000", "fffffffffffffff"),
    2: (64, 2, "0000000000000000", "ffffffffffffffff"),
}

print("\nEscolha a quantidade de bits para o prefixo:")
for k, v in bits_opcoes.items():
    print(f"{k} -> {v[0]} bits (prefixo com {v[1]} dígitos hex)")

op_bits = int(input("Digite a opção (1-8): ").strip())
if op_bits not in bits_opcoes:
    raise ValueError("Opção de bits inválida!")

bits_shift, hex_digitos, zeros_finais, ffs_finais = bits_opcoes[op_bits]

# Dados fornecidos
range_inicial_base = int("400000000000000000", 16)
range_final_base   = int("7fffffffffffffffff", 16)
inicio_pct = Decimal(input("Digite a porcentagem inicial: ").strip())
fim_pct    = Decimal(input("Digite a porcentagem final: ").strip())

# Tempo por comando
tempo_por_comando = float(input("Digite o tempo por comando (em segundos): ").strip())

# Calcular o espaço total
espaco_total = range_final_base - range_inicial_base

# Calcular valores inicial e final absolutos
valor_inicial = range_inicial_base + int((inicio_pct / Decimal(100)) * espaco_total)
valor_final   = range_inicial_base + int((fim_pct    / Decimal(100)) * espaco_total)

# Prefixos
inicio_prefixo = valor_inicial >> bits_shift
fim_prefixo    = valor_final >> bits_shift

# Parâmetros
ranges_por_arquivo = 10000
total_ranges = math.ceil((fim_prefixo - inicio_prefixo + 1) / incremento)
total_arquivos = math.ceil(total_ranges / ranges_por_arquivo)

# Cálculo do tempo total
total_segundos = total_ranges * tempo_por_comando
total_minutos = total_segundos / 60
total_horas = total_segundos / 3600

print(f"\n[+] Incremento escolhido: {incremento}")
print(f"[+] Bits escolhidos: {bits_shift} bits → prefixo com {hex_digitos} dígitos hex")
print(f"[+] Total de ranges: {total_ranges}")
print(f"[+] Tempo estimado:")
print(f"    Segundos: {total_segundos:,.0f} s")
print(f"    Minutos:  {total_minutos:,.2f} min")
print(f"    Horas:    {total_horas:,.2f} h")
print(f"[+] Serão gerados {total_arquivos} arquivos .sh\n")

# Criar pasta de saída
saida_dir = Path("ranges_split")
saida_dir.mkdir(exist_ok=True)

contador_range = 0
arquivo_idx = 1
f = None

prefixo = inicio_prefixo
while prefixo <= fim_prefixo:
    if contador_range % ranges_por_arquivo == 0:
        if f:
            f.close()
        arq_nome = saida_dir / f"range_{arquivo_idx}.sh"
        f = arq_nome.open("w")
        f.write("#!/bin/bash\n")
        arquivo_idx += 1

    inicio_hex = f"{prefixo:0{hex_digitos}x}{zeros_finais}"
    fim_hex    = f"{prefixo:0{hex_digitos}x}{ffs_finais}"
    f.write(
        f"timeout {int(tempo_por_comando)}s ./vanitysearch -stop -t 256 -gpu -gpuId 0,2,3,4,5,6,7,8,9,10,11,12,13 "
        f"-o out.txt -i 71.txt --keyspace {inicio_hex}:{fim_hex}\n"
    )
    f.write("sleep 2\n")

    contador_range += 1
    prefixo += incremento

if f:
    f.write(f"# Total de ranges neste arquivo: {contador_range % ranges_por_arquivo}\n")
    f.close()

print(f"[+] Arquivos gerados em: {saida_dir.resolve()}")
