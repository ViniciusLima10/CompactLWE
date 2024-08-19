import numpy as np
from sympy import mod_inverse, gcd
from scipy.linalg import lu, inv
import time

# Parâmetros Compact-LWE
q = 2**32
t = 2**16
m = 74
w = 86
n = 13
b = 16

# Função para gerar chaves (keygen)
def keygen():
    s = np.random.randint(0, q, n)  # Vetor s em Z_q^n
    r = np.random.randint(2, int(np.ceil(q / w / t)) - 1)  # r em um intervalo determinado
    assert r > b
    # Gerando p que seja coprimo com q
    p = 0
    while gcd(p, q) > 1:
        p = np.random.randint(t, int(np.ceil(q / r / w)) - 1)

    # Gerando sk que seja coprimo com q e p
    sk = 0
    while gcd(sk, q) > 1 or gcd(sk, p) > 1:
        sk = np.random.randint(1, int(np.ceil((q - w * r * p) / (t - 1))) - 1)
    assert sk < p
    # assert sk*(t-1) < p
    return s, r, p, sk

# Função para gerar amostras Compact-LWE (samplegen)
def samplegen(s, r, p, sk):
    A = np.random.randint(0, b, (m, n))  # Matriz A em Z_b^(m x n)
    k = (mod_inverse(p, q) * (-1) * sk) % q
    e = np.random.randint(0, r, m)  # Vetor de erros em Z_r^m

    # v = A*s + k*e
    v = (np.dot(A, s) + k * e) % q
    return A, v, e

# Função para criptografar (encrypt)
def encrypt(A, v, mu):
    a = np.random.randint(0, q, n)  # Vetor a
    x = mu
    for _ in range(w):
        j = np.random.randint(0, m)
        a = (a + A[j]) % q
        x = (x - v[j]) % q

    return a, x

def Dec(s, sk, p, a, d):
    # Passo 1: Calcular c' = ⟨a, s⟩ + d mod q
    c_prime = (np.dot(a, s) + d) % q
    
    # Passo 2: Calcular skv = sk × c' mod q
    skv = (sk * c_prime) % q
    
    # Passo 3: Calcular v = sk_p^{-1} × skv mod p
    sk_p_inverse = mod_inverse(sk, p)
    v = (sk_p_inverse * skv) % p
    
    # Verificação e ajustes para garantir a recuperação correta de mu
    if v < 0:
        v += p
    
    return v


# Exemplo de uso
if __name__ == "__main__":
    # Geração de chaves
    s, r, p, sk = keygen()

    # Geração de amostras Compact-LWE
    A, v, e = samplegen(s, r, p, sk)

    # Mensagem a ser criptografada
    mu = 1

    # Criptografia da mensagem
    a, x = encrypt(A, v, mu)

    v_dec = Dec(s, sk, p, a, x)
    print(f"Texto cifrado: {(a, x)}")
    print(f"Texto decifrado: {v_dec}")