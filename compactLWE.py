import numpy as np
from sympy import mod_inverse, gcd
from scipy.linalg import lu, inv
import math
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
    assert len(s) == n, f"Tamanho incorreto: esperado {n}, mas foi gerado {len(s)}"
    assert np.all((s >= 0) & (s < q)), f"Valores fora do intervalo: esperado entre 0 e {q-1}, mas foi gerado {s}"
    r = np.random.randint(2, int(np.ceil(q / w / t)) - 1)  # r em um intervalo determinado
    assert r > b
    # Gerando p que seja coprimo com q
    p = 0
    while gcd(p, q) > 1:
        p = np.random.randint(t, int(np.ceil(q / r / w)) - 1)
    assert math.gcd(p, q) == 1, f"{p} e {q} não são coprimos. O MDC é {math.gcd(p, q)}."
    # Gerando sk que seja coprimo com q e p
    sk = 0
    while gcd(sk, q) > 1 or gcd(sk, p) > 1:
        sk = np.random.randint(1, int(np.ceil((q - w * r * p) / (t - 1))) - 1)
    assert sk < p
    assert math.gcd(sk, p) == 1, f"{sk} e {p} não são coprimos. O MDC é {math.gcd(sk, p)}."
    assert math.gcd(sk, q) == 1, f"{sk} e {q} não são coprimos. O MDC é {math.gcd(p, q)}."
    assert t <= p
    assert sk*(t-1) + w *r *p < q
    return s, r, p, sk

# Função para gerar amostras Compact-LWE (samplegen)
def samplegen(s, r, p, sk):
    A = np.random.randint(0, b, (m, n))  # Matriz A em Z_b^(m x n)
    assert np.all((A >= 0) & (A < b)), f"Valores fora do intervalo em A: {A}"
    k = (mod_inverse(sk, q) * p) % q
    e = np.random.randint(0, r, m)  # Vetor de erros em Z_r^m
    assert np.all((e >= 0) & (e < r))

    # v = A*s + k*e
    v = (np.dot(A, s) + k * e) % q # v = pki

    assert np.all((np.dot(A, s) + e * k) % q == v), f"Erro no cálculo de v: {v}"
    return A, v, e

# Função para criptografar (encrypt)
def encrypt(A, v, mu):
    # Inicializando uma amostra aleatória (ai, pki) de PK
    
    # Escolher um índice aleatório inicial i e pegar a primeira amostra
    i = np.random.randint(0, m)
    a = A[i]  # Vetor ai da chave pública
    pk = v[i]  # Componente pk correspondente de v
    c_prime_a = a.copy()  # Inicializando c' com a parte ai
    c_prime_pk = pk       # Inicializando c' com a parte pki
    
    # Atualizar c_prime com w-1 amostras adicionais
    for _ in range(w - 1):
        j = np.random.randint(0, m)  # Escolher outro índice aleatório j
        c_prime_a = (c_prime_a + A[j]) % q  # Somando vetores ai + aj módulo q
        c_prime_pk = (c_prime_pk + v[j]) % q  # Somando pki + pkj módulo q
    
    # Finalização: calcular c = (a, v - pk mod q)
    a_final = c_prime_a  # Vetor a final
    x_final = (mu - c_prime_pk) % q  # Calculando x = (mu - pk mod q)
    
    return a_final, x_final

def Dec(s, sk, p, a, d):
    # Passo 1: Calcular c' = ⟨a, s⟩ + d mod q
    c_prime = ((np.dot(a, s) + d) % q)
    assert 0 <= c_prime < q, f"c_prime fora do intervalo [0, q-1]: {c_prime}"
    
    # Passo 2: Calcular skv = sk × c' mod q
    skv = (sk * c_prime) % q
    assert 0 <= skv < q, f"skv fora do intervalo [0, q-1]: {skv}"

    # Passo 3: Calcular v = sk_p^{-1} × skv mod p
    sk_p_inverse = mod_inverse(sk, p)
    v = (sk_p_inverse * skv) % p
    assert 0 <= v < p, f"v fora do intervalo [0, p-1]: {v}"
    
    # Verificação e ajustes para garantir a recuperação correta de mu
    if v < 0:
        v += p
    
    return v


# Exemplo de uso
if __name__ == "__main__":
    # Geração de chaves
    s, r, p, sk = keygen()
    print(f"s = {s}, r = {r}, p = {p}, sk = {sk}")

    # Geração de amostras Compact-LWE
    A, v, e = samplegen(s, r, p, sk)
    print(f"A = {A}, v = {v}, e = {e}")

    # Mensagem a ser criptografada
    mu = 1
    print(f"mu = {mu}")

    # Criptografia da mensagem
    a, x = encrypt(A, v, mu)
    print(f"a = {a}, x = {x}")

    v_dec = Dec(s, sk, p, a, x)
    print(f"v_dec = {v_dec}")
    print(f"Texto cifrado: {(a, x)}")
    print(f"Texto decifrado: {v_dec}")