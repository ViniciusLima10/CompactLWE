import numpy as np
import random

# ------------------------------
# Parâmetros do Ring-LWE
# ------------------------------
n = 8                  # Grau do polinômio (deve ser potência de 2)
q = 2**12              # Módulo primo ou potência de 2, suficientemente grande
sigma = 3.2            # Desvio da distribuição de erro (aprox.)

# ------------------------------
# Funções auxiliares
# ------------------------------

def poly_mul_mod(f, g):
    """
    Multiplica dois polinômios módulo (x^n + 1) e q
    """
    res = np.convolve(f, g)
    res_mod = np.zeros(n, dtype=int)

    for i in range(len(res)):
        if i < n:
            res_mod[i] += res[i]
        else:
            res_mod[i - n] -= res[i]  # x^n = -1

    return res_mod % q

def sample_error_poly():
    """
    Amostra erro com distribuição aproximadamente Gaussiana discreta
    """
    return np.array([
        int(sum(random.randint(0, 1) for _ in range(12)) - 6)
        for _ in range(n)
    ], dtype=int)

def sample_random_poly():
    """
    Amostra polinômio aleatório em Rq = Z_q[x]/(x^n + 1)
    """
    return np.random.randint(0, q, size=n, dtype=int)

def sample_message_poly():
    """
    Mensagem com coeficientes 0 ou 1
    """
    return np.random.choice([0, 1], size=n).astype(int)

# ------------------------------
# Algoritmo de Criptografia
# ------------------------------

def keygen():
    """
    Geração da chave secreta s ∈ Rq
    """
    return sample_random_poly()

def encrypt(m, s):
    """
    Criptografa a mensagem m usando segredo s.
    """
    a = sample_random_poly()
    e = sample_error_poly()
    half_q = q // 2

    b = (poly_mul_mod(a, s) + e + half_q * m) % q

    return a, b

def decrypt(a, b, s):
    """
    Decripta a mensagem usando segredo s.
    """
    rec = (b - poly_mul_mod(a, s)) % q

    # Converte para intervalo [-q/2, q/2)
    rec = np.array([coef - q if coef > q // 2 else coef for coef in rec])

    # Decodifica para 0 ou 1
    m_rec = np.array([1 if abs(coef) > q // 4 else 0 for coef in rec], dtype=int)
    return m_rec

# ------------------------------
# Execução de Teste
# ------------------------------

if __name__ == "__main__":
    print("=== Criptografia Ring-LWE ===")

    mensagem = sample_message_poly()
    print("Mensagem original:", mensagem)

    chave_secreta = keygen()
    a, b = encrypt(mensagem, chave_secreta)
    print("Cifrado a:", a)
    print("Cifrado b:", b)

    mensagem_rec = decrypt(a, b, chave_secreta)
    print("Mensagem decriptada:", mensagem_rec)

    if np.array_equal(mensagem, mensagem_rec):
        print(" Sucesso: Mensagem recuperada corretamente.")
    else:
        print("Falha: Mensagem incorreta.")
