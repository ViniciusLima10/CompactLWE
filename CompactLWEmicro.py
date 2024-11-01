import urandom
from math import log

# Função para calcular o inverso modular usando o Algoritmo Estendido de Euclides
def modular_inverse(a, m):
    m0, x0, x1 = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

# Função GCD (Máximo Divisor Comum)
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# Função para inversão modular usada no invk()
def invk(x, q):
    y = modular_inverse(x, q)
    return ((-1) * y) % q

# Soma de vetores com módulo q
def vecsum(a, b, q):
    n = len(a)
    return [(a[i] + b[i]) % q for i in range(n)]

# Produto escalar com módulo q
def dot(a, b, q):
    return sum((a[i] * b[i]) % q for i in range(len(a))) % q

# Gera um vetor aleatório de tamanho n com elementos no intervalo [0, q-1]
def genVector(n, q):
    return [urandom.getrandbits(8) % q for _ in range(n)]

# Função para gerar parâmetros públicos
def ppGen(q, n, t, w):
    m = urandom.getrandbits(8) % (n**2 - 1 - n) + n + 2
    b = urandom.getrandbits(8) % (2**(n // 2) - 1 - n) + n + 1
    assert (2 * log(b * b, 2) + 2) * b < q
    return q, n, m, t, w, b

# Geração da chave secreta com validações
def skGen(q, n, m, t, w, b):
    while True:
        s = genVector(n, q)
        r = urandom.getrandbits(8) % (2 * b) + b + 1
        sk = urandom.getrandbits(8) % (q // (2 * (t - 1)) - 1) + 2
        while gcd(sk, q) != 1:
            sk = urandom.getrandbits(8) % (q // (2 * (t - 1)) - 1) + 2
        p = urandom.getrandbits(8) % (q // (2 * w * r) - 1 + t) + t
        while gcd(p, sk) != 1 or gcd(p, q) != 1:
            p = urandom.getrandbits(8) % (q // (2 * w * r) - 1 + t) + t

        # Checar se todas as condições dos asserts são satisfeitas
        if (t <= p and
            gcd(p, q) == 1 and
            gcd(p, sk) == 1 and
            gcd(q, sk) == 1 and
            sk * (t - 1) + w * r * p < q and
            b < r < q and sk < q and p < q):
            break  # Prosseguir apenas se todas as condições forem verdadeiras

    return s, sk, r, p

# Gera chave pública a partir da chave secreta
def pkGen(sk, p, q, s, b, m, n, r):
    PK = []
    for i in range(m):
        a = genVector(n, b)
        e = urandom.getrandbits(8) % (r - 1) + 1
        skq = invk(sk, q)
        pk = (dot(a, s, q) + e * skq * p) % q
        PK.append((a, pk))
    return PK

# Função de encriptação
def encrypt(v, PK, p, q, m, n, w):
    C = [[0 for _ in range(n)], 0]
    for j in range(w):
        i = urandom.getrandbits(8) % m
        C[0] = vecsum(C[0], PK[i][0], q)
        C[1] = (C[1] + PK[i][1]) % q
    C[1] = (v - C[1]) % q
    return C

# Função de descriptografia
def decrypt(C, s, sk, r, p, q):
    a = C[0]
    d = C[1]
    cp = (dot(a, s, q) + d) % q
    skv = (sk * cp) % q
    skp = modular_inverse(sk, p)
    dec = (skp * skv) % p
    return dec

# Função de teste para verificar criptografia e descriptografia
def test(v):
    q = 2**32
    t = 2**16
    m = 74
    w = 86
    n = 13
    b = 16

    s, sk, r, p = skGen(q, n, m, t, w, b)
    PK = pkGen(sk, p, q, s, b, m, n, r)
    C = encrypt(v, PK, p, q, m, n, w)
    D = decrypt(C, s, sk, r, p, q)

    if D != v:
        print("Erro na decodificação!")
    else:
        print("Sucesso na decodificação!")

# Executa o teste para múltiplos valores
for i in range(10):  # Reduzido para 10 testes para evitar demora
    v = urandom.getrandbits(16)
    test(v)
