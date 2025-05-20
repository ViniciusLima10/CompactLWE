import numpy as np
import logging
import time
from fpylll import IntegerMatrix, LLL

# ----------------- CONFIGURAÇÃO DO LOG -----------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RingLWE-Attack")

# ----------------- PARÂMETROS INICIAIS -----------------
n = 8
q = 2 ** 12

# ----------------- FUNÇÕES AUXILIARES -----------------

def sample_message_poly():
    return np.random.choice([0, 1], size=n).astype(int)

def keygen():
    return np.random.randint(0, q, size=n, dtype=int)

def encrypt(mensagem, s):
    a = np.random.randint(0, q, size=n, dtype=int)
    e = np.random.randint(-1, 2, size=n, dtype=int)
    b = (np.convolve(a, s, mode="same") + e + mensagem) % q
    return a, b

def construir_lattice(a, b, kappa=None):
    if kappa is None:
        kappa = q

    dim = n + 2
    A = IntegerMatrix(dim, dim)

    A[0, 0] = 1
    for i in range(n):
        A[0, i + 2] = int(kappa * a[i])

    for i in range(n):
        A[i + 1, 1] = 1
        A[i + 1, i + 2] = -int(kappa)
        A[i + 1, -1] = int(b[i])

    A[n + 1, -1] = int(q)
    return A

def ataque_lll(a, b):
    M = construir_lattice(a, b)
    Mred = LLL.reduction(M)

    for row in Mred:
        if abs(row[0]) == 1:
            return int(row[-1] // row[0]) % q
    return None

def interpretar(valor):
    if valor is None:
        return None
    return 1 if abs(valor - q // 2) < q // 4 else 0

# ----------------- LOOP INFINITO COM ESCALONAMENTO -----------------

while True:
    try:
        mensagem = sample_message_poly()
        s = keygen()
        a, b = encrypt(mensagem, s)

        start = time.time()
        estimado = ataque_lll(a, b)
        estimado_bit = interpretar(estimado)
        tempo = time.time() - start

        if estimado_bit is None:
            logger.warning(f"n={n}: LLL falhou, tempo={tempo:.2f}s")
        elif estimado_bit == mensagem[0]:
            logger.info(f"n={n}: Sucesso, tempo={tempo:.2f}s")
        else:
            logger.warning(f"n={n}: Ataque falhou (bit incorreto), tempo={tempo:.2f}s")

        # Aumenta o parâmetro de segurança
        n += 20

    except KeyboardInterrupt:
        logger.info("Execução interrompida pelo usuário.")
        break
