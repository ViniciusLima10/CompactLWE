from sage.all import *

# Compact-LWE parameters
q = 2^32
t = 2^16
m = 22
w = 86
n = 20
b = 21
R = Integers(q)

# Key generation function
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

# Sample generation function
def samplegen(s, r, p, sk):
    A = random_matrix(ZZ, m, n, x=0, y=b)
    k = R(p) / R(sk)
    e = vector(R, [randint(0, r - 1) for _ in range(m)])
    v = A * s + k * e
    return A, v.change_ring(ZZ), e

# Encryption function
def encrypt(A, v, mu):
    a = vector(R, n)
    x = R(mu)
    for _ in range(w):
        j = randint(0, m - 1)
        a += A[j]
        x -= v[j]
    return a.change_ring(ZZ), x.lift()

# Subset sum decryption attack function
def subsetsumdecrypt(A, v, a, x):
    kappa = q
    L = block_matrix(ZZ, [
        [1, 0, kappa * a.row(), x],
        [0, t * identity_matrix(m), -kappa * A, v.column()],
        [0, 0, 0, q]
    ])
    L = L.LLL()
    
    # Index of the first non-zero entry in the first column of L
    idx = next((i for i, x in enumerate(L.column(0).list()) if x != 0))
    g = gcd(L[:idx, -1].list())
    cand = L[idx, -1] // L[idx, 0]
    if g > t:
        cand = cand % g
    return L, cand

# Test function for the decryption attack
def testsubsetsumdecrypt(trials=100, pairs=1):
    succ = 0
    tottime = 0.0
    for npair in range(pairs):
        s, r, p, sk = keygen()
        A, v, e = samplegen(s, r, p, sk)
        succnow = 0
        for _ in range(trials):
            mu = randint(1, t - 1)
            a, x = encrypt(A, v, mu)
            tm = cputime(subprocesses=True)
            mucand = subsetsumdecrypt(A, v, a, x)[1]
            tottime += float(cputime(tm))
            if mu == mucand:
                succnow += 1
        succ += succnow
        print("Key pair %d complete. Success rate: %d/%d." % (npair, succnow, trials))
    print("Successful recoveries: %d/%d (%f)." % (succ, trials * pairs, RR(100 * succ / trials / pairs)))
    print("Average time: %f seconds." % (tottime / trials / pairs))

# Run the test
testsubsetsumdecrypt(1, 1)
