import numpy as np

# ------------------------------
# Configurações principais
# ------------------------------
# Grau do polinômio (n deve ser potência de 2)
n = 8
# Modulo q 
q = 2**32

# Espaço de mensagens: polinômios com coeficientes 0 ou 1
# Erro: distribuição pequena de números (-1, 0, 1)
def sample_error_poly():
    return np.random.choice([-1, 0, 1], size=n, p=[0.1, 0.8, 0.1])

# Geração de polinômio aleatório no anel Rq
def sample_random_poly():
    return np.random.randint(0, q, size=n)

# Produto de dois polinômios módulo (x^n + 1) e q
# Usa convolução circular
def poly_mul_mod(a, b):
    res = np.convolve(a, b)
    # Reduz modulo (x^n + 1)
    res_mod = np.zeros(n, dtype=int)
    for i in range(len(res)):
        if i < n:
            res_mod[i] += res[i]
        else:
            res_mod[i - n] -= res[i]  # "-" porque x^n = -1
    return res_mod % q

# ------------------------------
# Algoritmo de Criptografia
# ------------------------------

def keygen():
    """
    Gera uma chave secreta aleatória.
    """
    s = sample_random_poly()
    return s

def encrypt(m, s):
    """
    Criptografa a mensagem m usando o segredo s.
    """
    a = sample_random_poly()  # elemento aleatório
    e = sample_error_poly()   # erro pequeno
    half_q = q // 2

    # Computa b = a * s + e + (q/2) * m mod q
    b = (poly_mul_mod(a, s) + e + half_q * m) % q
    
    return (a, b)

def decrypt(a, b, s):
    """
    Decripta o par (a, b) usando o segredo s.
    """
    # Computa b - a*s mod q

    rec = (b - poly_mul_mod(a, s)) % q
    
    # Decodifica: se o coeficiente está mais perto de q/2 -> 1, senão -> 0
    threshold = q // 4
    m_rec = np.array([1 if coef > q//2 - threshold and coef < q//2 + threshold else 0 for coef in rec])
    return m_rec


# ------------------------------
# Teste de exemplo
# ------------------------------
if __name__ == "__main__":
    print("Iniciando Ring-LWE Criptografia!")

    # Mensagem aleatória (0 ou 1 em cada posição)
    mensagem = np.random.choice([0, 1], size=n)
    print(f"Mensagem original: {mensagem}")

    # Gera a chave secreta
    chave_secreta = keygen()

    # Criptografa a mensagem
    a, b = encrypt(mensagem, chave_secreta)
    print(f"Cifrado (a): {a}")
    print(f"Cifrado (b): {b}")

    # Decripta a mensagem
    mensagem_recuperada = decrypt(a, b, chave_secreta)
    print(f"Mensagem decriptada: {mensagem_recuperada}")

    # Verifica se a mensagem foi recuperada corretamente
    if np.array_equal(mensagem, mensagem_recuperada):
        print("Sucesso: a mensagem foi recuperada corretamente!")
    else:
        print("Falha: a mensagem não foi recuperada corretamente.")

