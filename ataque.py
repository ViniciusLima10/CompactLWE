from sage.all import *

# Parâmetros Compact-LWE
q = 2^32
t = 2^16
m = 74
w = 86
n = 13
b = 16
R = Integers(q)

# Função para gerar chaves (keygen)
def keygen():
    s = vector(R, [R.random_element() for _ in range(n)])
    
    # Ajuste do cálculo para garantir que r tenha um intervalo válido
    r_min = max(2, ceil(q / w / t) - 1)  # Garante que r_min seja pelo menos 2
    r = randint(r_min, max(r_min + 1, r_min + 10))  # Pequeno intervalo para evitar ranges vazios

    p = 0
    while gcd(p, q) > 1:
        p = randint(t, ceil(q / r / w) - 1)

    sk = 0
    while gcd(sk, q) > 1 or gcd(sk, p) > 1:
        sk = randint(1, ceil((q - w * r * p) / (t - 1)) - 1)

    return s, r, p, sk


# Função para gerar amostras Compact-LWE (samplegen)
def samplegen(s, r, p, sk):
    A = random_matrix(ZZ, m, n, x = 0, y = b)
    k = R(p) / R(sk)
    e = vector(R, [randint(0, r - 1) for _ in range(m)])
    v = A * s + k * e
    return A, v.change_ring(ZZ), e

# Função para criptografar (encrypt)
def encrypt(A, v, mu):
    a = vector(R, n)
    x = R(mu)
    for _ in range(w):
        j = randint(0, m - 1)
        a += A[j]
        x -= v[j]

    return a.change_ring(ZZ), x.lift()

# Função para descriptografia usando ataque de subset sum (subsetsumdecrypt)
def subsetsumdecrypt(A, v, a, x):
    kappa = q

    L = block_matrix(ZZ, [
        [1, 0, kappa * a.row(), x],
        [0, t * identity_matrix(m), -kappa * A, v.column()],
        [0, 0, 0, q]
    ])
    L = L.LLL()

    # Índice da primeira entrada não-nula na primeira coluna de L
    idx = next((i for i, x in enumerate(L.column(0).list()) if x != 0))
    g = gcd(L[idx, -1], L[idx, 0])
    cand = L[idx, -1] // L[idx, 0]
    if g > 1:
        cand = cand % g

    return L, cand

# Função principal (main) para realizar todo o processo
def main():
    # Geração de chaves
    print("Gerando chaves...")
    s, r, p, sk = keygen()
    print(f"Chaves geradas:\ns = {s}\nr = {r}\np = {p}\nsk = {sk}\n")

    # Geração de amostras Compact-LWE
    print("Gerando amostras LWE...")
    A, v, e = samplegen(s, r, p, sk)
    print(f"Amostras LWE geradas:\nA = {A}\nv = {v}\ne = {e}\n")

    # Mensagem a ser criptografada
    mu = 1
    print(f"Criptografando a mensagem: {mu}...")
    a, x = encrypt(A, v, mu)
    print(f"Texto cifrado: (a = {a}, x = {x})\n")

    # Realizando o ataque de subset sum
    print("Executando o ataque de subset sum...")
    _, v_ataque = subsetsumdecrypt(A, v, a, x)
    print(f"Texto recuperado com ataque: {v_ataque}\n")

    # Comparação dos resultados
    if mu == v_ataque:
        print("Ataque bem-sucedido: a mensagem foi recuperada corretamente!")
    else:
        print("Ataque falhou: a mensagem recuperada não corresponde à original.")


main()
