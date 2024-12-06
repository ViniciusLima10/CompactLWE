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

# Função para geração da chave secreta com validações
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

# Loop infinito para ajustar os parâmetros e testar o limite do dispositivo
def find_max_parameters():
    # Parâmetros iniciais
    q = 2**12  # Início com valor mais baixo para evitar overflow
    n = 4
    m = n + 2
    t = 2**8
    w = 10  # Parâmetro menor para minimizar uso de memória
    b = n + 1

    while True:
        # Garante que m e b estão no intervalo exigido
        m = min(m, n**2 - 1)
        b = min(b, q - 1)

        # Verifica a condição (2 * log(b) * b + 2) * b < q
        if (2 * log(b, 2) * b + 2) * b < q and 2 * log(b, 2) < n:
            # Executa o teste com os parâmetros atuais
            v = urandom.getrandbits(8) % (t - 1)
            try:
                s, sk, r, p = skGen(q, n, m, t, w, b)
                PK = pkGen(sk, p, q, s, b, m, n, r)
                C = encrypt(v, PK, p, q, m, n, w)
                D = decrypt(C, s, sk, r, p, q)

                # Imprime os parâmetros atuais
                print("Parâmetros atuais:")
                print(f"q = {q}, n = {n}, m = {m}, t = {t}, w = {w}, b = {b}")

                # Verifica se a decodificação foi bem-sucedida
                if D == v:
                    print("Sucesso na decodificação! Aumentando parâmetros...\n")
                    # Aumenta os parâmetros para o próximo teste
                    q = min(q * 2, 2**18)  # Limite para evitar estouro de memória
                    n = min(n + 1, 32)     # Limite máximo de n para minimizar o uso de memória
                    m = n + 2
                    b = n + 1
                else:
                    print("Falha na decodificação. Mantendo parâmetros.")
            except Exception as e:
                print("Erro na execução:", e)
                break  # Encerra o loop em caso de erro
        else:
            print("Condições para parâmetros não atendidas. Ajustando...")
            n = min(n + 1, 32)
            m = n + 2
            b = n + 1
            q = min(q * 2, 2**18)

# Inicia a busca pelos maiores parâmetros
find_max_parameters()
