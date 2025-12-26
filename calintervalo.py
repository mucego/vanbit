import time

def calcular_tempo(chave_inicial, chave_final, chaves_por_segundo):
    # Converter as chaves hexadecimais para inteiros
    chave_inicial_int = int(chave_inicial, 16)
    chave_final_int = int(chave_final, 16)

    # Calcular o número de chaves no intervalo
    total_chaves = chave_final_int - chave_inicial_int

    # Calcular o tempo necessário em segundos
    tempo_segundos = total_chaves / chaves_por_segundo

    # Converter o tempo para dias, horas, minutos e segundos
    dias = tempo_segundos // 86400
    horas = (tempo_segundos % 86400) // 3600
    minutos = (tempo_segundos % 3600) // 60
    segundos = tempo_segundos % 60

    # Formatando a resposta
    return f"{int(dias)} days, {int(horas)}:{int(minutos):02}:{int(segundos):02}"

# Entrada de dados
chave_inicial = input("Digite a chave hexadecimal inicial (ex: 7628200000000000): ")
chave_final = input("Digite a chave hexadecimal final (ex: 76282ffffffffff): ")
chaves_por_segundo = int(input("Digite o número de chaves por segundo (ex: 2000000000): "))

# Calcular o tempo necessário
tempo_necessario = calcular_tempo(chave_inicial, chave_final, chaves_por_segundo)

# Exibir o resultado
print(f"Tempo Necessário: {tempo_necessario}")
