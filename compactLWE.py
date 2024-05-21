import random
from math import gcd

# Variáveis globais fixas
q = 4294967296
n = 13
m = 74
t = 65536
w = 86
b = 16

# Função para encontrar o inverso modular
def modinv(a, mod):
    t, new_t = 0, 1
    r, new_r = mod, a
    while new_r != 0:
        quotient = r // new_r
        t, new_t = new_t, t - quotient * new_t
        r, new_r = new_r, r - quotient * new_r
    if r > 1:
        raise ValueError("a is not invertible")
    if t < 0:
        t = t + mod
    return t

# Função Gen
def Gen():
    # Gerar s, vetor n-dimensional com coordenadas mod q
    s = [random.randint(0, q-1) for _ in range(n)]
    
    # Encontrar sk, r e p que satisfazem as condições
    while True:
        sk = random.randint(1, q-1)
        r = random.randint(b + 1, q-1)
        p = random.randint(t, q-1)
        
        # Verificar se sk, p e q são coprimos
        if gcd(sk, p) == 1 and gcd(sk, q) == 1 and gcd(p, q) == 1:
            # Verificar a condição sk * (t - 1) + w * r * p < q
            if sk * (t - 1) + w * r * p < q:
                break
    
    # Calcular sk^-1?q que satisfaz a condição sk * sk^-1?q = -1 mod q
    sk_inv_q = modinv(sk, q)
    sk_inv_q = (-sk_inv_q) % q
    
    # Calcular k
    k = (sk_inv_q * p) % q
    
    K = (s, sk, r, p)
    
    # Gerar ai e calcular pki
    ai = [[random.randint(0, b-1) for _ in range(n)] for _ in range(m)]
    PK = []
    for a in ai:
        ei = random.randint(0, r-1)
        inner_product = sum(a[i] * s[i] for i in range(n)) % q
        pki = (inner_product + ei * k) % q
        PK.append((a, pki))
    
    return K, PK

# Função Enc
def Enc(PK, v):
    # Escolha um número inteiro i uniformemente de {1, ..., m}
    i = random.randint(0, m-1)
    c_prime = PK[i]
    
    # Amostrar w inteiros uniformemente de {1, ..., m}
    for _ in range(w):
        j = random.randint(0, m-1)
        a_prime = [(c_prime[0][k] + PK[j][0][k]) % q for k in range(n)]
        pk_prime = (c_prime[1] + PK[j][1]) % q
        c_prime = (a_prime, pk_prime)
    
    # Suponha que c' = (a, pk) e gere c = (a, v - pk mod q)
    a, pk = c_prime
    c = (a, (v - pk) % q)
    
    return c

# Função Dec
def Dec(K, c):
    (s, sk, r, p) = K
    (a, d) = c
    
    # Calcular c' = produtoInterno(a, s) + d mod q
    inner_product = sum(a[i] * s[i] for i in range(n)) % q
    c_prime = (inner_product + d) % q
    
    # Calcular skv = sk * c' mod q
    skv = (sk * c_prime) % q
    
    # Calcular sk^-1?p
    sk_inv_p = modinv(sk, p)
    
    # Calcular v = sk^-1?p * skv mod p
    v = (sk_inv_p * skv) % p
    
    return v

# Executar a função Gen para obter K e PK
K, PK = Gen()
print("K:", K)
print("PK:")
for pk in PK:
    print(pk)

# Testar a função Enc e Dec
v = 1  # Valor a ser encriptado
c = Enc(PK, v)
print("Valor encriptado (c):", c)

# Descriptografar o valor
v_recuperado = Dec(K, c)
print("Valor recuperado (v):", v_recuperado)
