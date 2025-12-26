def is_valid_hex_key(key):
    """Verifica se a chave é um hexadecimal de 18 dígitos."""
    if len(key) != 18:
        return False
    try:
        int(key, 16)
        return True
    except ValueError:
        return False

def calculate_percentage(key, range_start, range_end):
    """Calcula a porcentagem da chave dentro do intervalo com 18 casas decimais."""
    key_int = int(key, 16)
    start_int = int(range_start, 16)
    end_int = int(range_end, 16)
    
    if key_int < start_int or key_int > end_int:
        return None  # Chave fora do intervalo
    
    range_size = end_int - start_int
    position = key_int - start_int
    percentage = (position / range_size) * 100
    
    # Formata com 18 casas decimais
    return f"{percentage:.18f}"

def main():
    range_start = "400000000000000000"
    range_end = "7fffffffffffffffff"
    
    while True:
        key = input("Digite uma chave hexadecimal de 18 dígitos (ou 'sair' para encerrar): ").strip()
        
        if key.lower() == 'sair':
            print("Programa encerrado.")
            break
            
        if not is_valid_hex_key(key):
            print("Erro: A chave deve ter exatamente 18 dígitos hexadecimais válidos.")
            continue
            
        percentage = calculate_percentage(key, range_start, range_end)
        
        if percentage is None:
            print(f"Erro: A chave {key} está fora do intervalo [{range_start}, {range_end}].")
        else:
            print(f"A chave {key} está a {percentage}% do intervalo.")

if __name__ == "__main__":
    main()