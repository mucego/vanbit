def is_valid_percentage(percentage_str):
    """Verifica se a entrada é uma porcentagem válida (0 a 100)."""
    try:
        percentage = float(percentage_str)
        if 0 <= percentage <= 100:
            return True
        return False
    except ValueError:
        return False

def calculate_key_from_percentage(percentage, range_start, range_end):
    """Calcula a chave hexadecimal correspondente à porcentagem no intervalo."""
    percentage = float(percentage)
    start_int = int(range_start, 16)
    end_int = int(range_end, 16)
    
    range_size = end_int - start_int
    position = int((percentage / 100) * range_size)
    key_int = start_int + position
    
    # Converte para hexadecimal, remove o prefixo '0x' e garante 18 dígitos
    key_hex = format(key_int, '018x').upper()
    return key_hex

def main():
    range_start = "400000000000000000"
    range_end = "7fffffffffffffffff"
    
    while True:
        percentage = input("Digite uma porcentagem (0 a 100, ou 'sair' para encerrar): ").strip()
        
        if percentage.lower() == 'sair':
            print("Programa encerrado.")
            break
            
        if not is_valid_percentage(percentage):
            print("Erro: A porcentagem deve ser um número válido entre 0 e 100.")
            continue
            
        key = calculate_key_from_percentage(percentage, range_start, range_end)
        print(f"A porcentagem {percentage}% corresponde à chave: {key}")

if __name__ == "__main__":
    main()