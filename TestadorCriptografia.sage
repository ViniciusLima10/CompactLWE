from sage.all import *
import time
import os
import pandas as pd

# Compact-LWE parameters (valores iniciais)
q = 2^32
t = 2^16
R = Integers(q)

# Função para verificar parâmetros
def verificar_parametros(n, m, b):
    return (
        n + 1 < m < n**2 and
        n < b and
        ((2 * log(b, 2) * b + 2) * b) < q and
        (2 * log(b, 2)) < n
    )

# Funções do algoritmo (mantidas exatamente como fornecidas)
def keygen():
    s = vector(R, [R.random_element() for _ in range(n)])
    r = randint(2, ceil(q / w / t) - 1)
    p = 0
    while gcd(p, q) > 1:
        p = randint(t, ceil(q / r / w) - 1)
    sk = 0
    while gcd(sk, q) > 1 or gcd(sk, p) > 1:
        sk = randint(1, ceil((q - w * r * p) / (t - 1)) - 1)
    return s, r, p, sk

def samplegen(s, r, p, sk):
    A = random_matrix(ZZ, m, n, x=0, y=b)
    k = R(p) / R(sk)
    e = vector(R, [randint(0, r - 1) for _ in range(m)])
    v = A * s + k * e
    return A, v.change_ring(ZZ), e

def encrypt(A, v, mu):
    a = vector(R, n)
    x = R(mu)
    for _ in range(w):
        j = randint(0, m - 1)
        a += A[j]
        x -= v[j]
    return a.change_ring(ZZ), x.lift()

def subsetsumdecrypt(A, v, a, x):
    kappa = q
    L = block_matrix(ZZ, [
        [1, 0, kappa * a.row(), x],
        [0, t * identity_matrix(m), -kappa * A, v.column()],
        [0, 0, 0, q]
    ])
    L = L.LLL()
    idx = next((i for i, x in enumerate(L.column(0).list()) if x != 0))
    g = gcd(L[:idx, -1].list())
    cand = L[idx, -1] // L[idx, 0]
    if g > t:
        cand = cand % g
    return L, cand

def carregar_estado():
    # Verifica o arquivo estado.txt
    if os.path.exists("estado.txt"):
        with open("estado.txt", "r") as arquivo:
            conteudo = arquivo.read().strip()
            if conteudo.isdigit():
                print(f"Estado carregado: N = {conteudo}")  # Depuração
                return int(conteudo)

    # Verifica o arquivo resultados.txt
    if os.path.exists("resultados.txt"):
        try:
            with open("resultados.txt", "r") as arquivo:
                linhas = arquivo.readlines()
                for linha in reversed(linhas[1:]):  # Ignora o cabeçalho
                    valores = linha.strip().split(",")
                    if valores and valores[0].isdigit():
                        n = int(valores[0])
                        print(f"Recuperado do arquivo resultados.txt: N = {n}")  # Depuração
                        return n
        except Exception as e:
            print(f"Erro ao carregar resultados.txt: {e}")

    # Caso nenhum estado válido seja encontrado
    print("Nenhum estado válido encontrado. Iniciando com N = 20.")
    return 20


# Salvar o estado atual no arquivo
def salvar_estado(n):
    with open("estado.txt", "w") as arquivo:
        arquivo.write(str(n))

# Loop principal
def loop_infinito():
    global n, m, w, b
    n = carregar_estado()  # Carregar o estado inicial
    with open("resultados.txt", "a") as arquivo:  # Abre o arquivo em modo append
        if os.stat("resultados.txt").st_size == 0:
            arquivo.write("N,M,B,Tempo\n")  # Cabeçalho apenas se o arquivo estiver vazio
        while True:
            n += 1  # Incrementa N
            salvar_estado(n)  # Salvar o estado atual
            for m in range(n + 1, n**2):
                for b in range(n + 1, n**2):
                    if verificar_parametros(n, m, b):
                        w = 86  # Parâmetro fixo
                        try:
                            # Executa o algoritmo com os parâmetros válidos
                            s, r, p, sk = keygen()
                            A, v, e = samplegen(s, r, p, sk)
                            mu = randint(1, t - 1)
                            a, x = encrypt(A, v, mu)
                            start_time = time.time()
                            _, mucand = subsetsumdecrypt(A, v, a, x)
                            end_time = time.time()
                            tempo = end_time - start_time

                            # Salva resultados
                            arquivo.write(f"{n},{m},{b},{tempo:.4f}\n")
                            arquivo.flush()
                            print(f"N={n}, M={m}, B={b}, Tempo={tempo:.4f} segundos")
                        except Exception as e:
                            print(f"Erro com N={n}, M={m}, B={b}: {e}")
                        break
                else:
                    continue
                break

# Executa o loop
loop_infinito()
