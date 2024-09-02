import re

def validar_cpf(cpf):
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11:
        return False
    # Validação do CPF
    def calcular_digito(digs):
        soma = sum(int(dig) * peso for dig, peso in zip(digs, range(len(digs)+1, 1, -1)))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)
    return cpf[-2:] == calcular_digito(cpf[:-2]) + calcular_digito(cpf[:-1])

def validar_email(email):
    padrao_email = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(padrao_email, email) is not None

def validar_telefone(telefone):
    padrao_telefone = r'^\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}$'
    return re.match(padrao_telefone, telefone) is not None

def verificar_string(string):
    if validar_cpf(string):
        return True, "cpf"
    elif validar_email(string):
        return True, "email"
    elif validar_telefone(string):
        return True, "Telefone"
    else:
        return "Formato desconhecido"

# Exemplo de uso
#entrada = input("Digite uma string para verificar: ")
#resultado = verificar_string(entrada)
#print(resultado)
