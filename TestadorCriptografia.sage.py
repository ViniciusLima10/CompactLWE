

# This file was *autogenerated* from the file TestadorCriptografia.sage
from sage.all_cmdline import *   # import sage library

_sage_const_2 = Integer(2); _sage_const_32 = Integer(32); _sage_const_16 = Integer(16); _sage_const_1 = Integer(1); _sage_const_0 = Integer(0); _sage_const_20 = Integer(20); _sage_const_86 = Integer(86)
from sage.all import *
import time
import os
import pandas as pd

# Compact-LWE parameters (valores iniciais)
q = _sage_const_2 **_sage_const_32 
t = _sage_const_2 **_sage_const_16 
R = Integers(q)

# Função para verificar parâmetros
def verificar_parametros(n, m, b):
    return (
        n + _sage_const_1  < m < n**_sage_const_2  and
        n < b and
        ((_sage_const_2  * log(b, _sage_const_2 ) * b + _sage_const_2 ) * b) < q and
        (_sage_const_2  * log(b, _sage_const_2 )) < n
    )

# Funções do algoritmo (mantidas exatamente como fornecidas)
def keygen():
    s = vector(R, [R.random_element() for _ in range(n)])
    r = randint(_sage_const_2 , ceil(q / w / t) - _sage_const_1 )
    p = _sage_const_0 
    while gcd(p, q) > _sage_const_1 :
        p = randint(t, ceil(q / r / w) - _sage_const_1 )
    sk = _sage_const_0 
    while gcd(sk, q) > _sage_const_1  or gcd(sk, p) > _sage_const_1 :
        sk = randint(_sage_const_1 , ceil((q - w * r * p) / (t - _sage_const_1 )) - _sage_const_1 )
    return s, r, p, sk

def samplegen(s, r, p, sk):
    A = random_matrix(ZZ, m, n, x=_sage_const_0 , y=b)
    k = R(p) / R(sk)
    e = vector(R, [randint(_sage_const_0 , r - _sage_const_1 ) for _ in range(m)])
    v = A * s + k * e
    return A, v.change_ring(ZZ), e

def encrypt(A, v, mu):
    a = vector(R, n)
    x = R(mu)
    for _ in range(w):
        j = randint(_sage_const_0 , m - _sage_const_1 )
        a += A[j]
        x -= v[j]
    return a.change_ring(ZZ), x.lift()

def subsetsumdecrypt(A, v, a, x):
    kappa = q
    L = block_matrix(ZZ, [
        [_sage_const_1 , _sage_const_0 , kappa * a.row(), x],
        [_sage_const_0 , t * identity_matrix(m), -kappa * A, v.column()],
        [_sage_const_0 , _sage_const_0 , _sage_const_0 , q]
    ])
    L = L.LLL()
    idx = next((i for i, x in enumerate(L.column(_sage_const_0 ).list()) if x != _sage_const_0 ))
    g = gcd(L[:idx, -_sage_const_1 ].list())
    cand = L[idx, -_sage_const_1 ] // L[idx, _sage_const_0 ]
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
                for linha in reversed(linhas[_sage_const_1 :]):  # Ignora o cabeçalho
                    valores = linha.strip().split(",")
                    if valores and valores[_sage_const_0 ].isdigit():
                        n = int(valores[_sage_const_0 ])
                        print(f"Recuperado do arquivo resultados.txt: N = {n}")  # Depuração
                        return n
        except Exception as e:
            print(f"Erro ao carregar resultados.txt: {e}")

    # Caso nenhum estado válido seja encontrado
    print("Nenhum estado válido encontrado. Iniciando com N = 20.")
    return _sage_const_20 


# Salvar o estado atual no arquivo
def salvar_estado(n):
    with open("estado.txt", "w") as arquivo:
        arquivo.write(str(n))

# Loop principal
def loop_infinito():
    global n, m, w, b
    n = carregar_estado()  # Carregar o estado inicial
    with open("resultados.txt", "a") as arquivo:  # Abre o arquivo em modo append
        if os.stat("resultados.txt").st_size == _sage_const_0 :
            arquivo.write("N,M,B,Tempo\n")  # Cabeçalho apenas se o arquivo estiver vazio
        while True:
            n += _sage_const_1   # Incrementa N
            salvar_estado(n)  # Salvar o estado atual
            for m in range(n + _sage_const_1 , n**_sage_const_2 ):
                for b in range(n + _sage_const_1 , n**_sage_const_2 ):
                    if verificar_parametros(n, m, b):
                        w = _sage_const_86   # Parâmetro fixo
                        try:
                            # Executa o algoritmo com os parâmetros válidos
                            s, r, p, sk = keygen()
                            A, v, e = samplegen(s, r, p, sk)
                            mu = randint(_sage_const_1 , t - _sage_const_1 )
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
