from Crypto.Util import number

from random import randint

from math import log



def invk(x,q):

    y = number.inverse(x,q)

    return ((-1)*y)%q



def vecsum(a,b,q):

    n = len(a)

    c = [0 for i in range(n)]

    for i in range(n):

        c[i] = (a[i] + b[i])%q

    return c



def dot(a,b,q):

    n = len(a)

    s = 0

    for i in range(n):

        s = (s + a[i]*b[i])%q

    return s



def genVector(n,q):

    v = []

    for i in range(n):

        v.append(randint(0,q-1))

    return v



def ppGen(q,n,t,w):

    m = randint(n+2,n**2-1)

    b = randint(n+1,int(2**(n/2)-1))

    assert (2*log(b*b,2) + 2)*b < q

    return q,n,m,t,w,b



def skGen(q, n, m, t, w, b):
    while True:
        s = genVector(n, q)
        r = randint(b + 1, 2 * b)
        sk = randint(2, int(q / (2 * (t - 1))) - 1)
        while number.GCD(sk, q) != 1:
            sk = randint(2, int(q / (2 * (t - 1))) - 1)
        p = randint(t, int(q / (2 * w * r)) - 1 + t)
        while number.GCD(p, sk) != 1 or number.GCD(p, q) != 1:
            p = randint(t, int(q / (2 * w * r)) - 1 + t)

        # Checar se todas as condições dos asserts são satisfeitas
        if (t <= p and
            number.GCD(p, q) == 1 and
            number.GCD(p, sk) == 1 and
            number.GCD(q, sk) == 1 and
            sk * (t - 1) + w * r * p < q and
            b < r < q and
            sk < q and
            p < q):
            break  # Prosseguir apenas se todas as condições forem verdadeiras

    return s, sk, r, p




def pkGen(sk,p,q,s,b,m,n,r):

    PK = []

    for i in range(m):

        a = genVector(n,b)

        e = randint(1,r-1)

        skq = invk(sk,q)

        pk = (dot(a,s,q) + e*skq*p)%q

        PK.append((a,pk))

    return PK



def encrypt(v,PK,p,q,m,n,w):

    C = [[0 for i in range(n)],0]

    for j in range(w):

        i = randint(0,m-1)

        C[0] = vecsum(C[0],PK[i][0],q)

        C[1] = (C[1] + PK[i][1])%q

    C[1] = (v - C[1])%q

    return C



def decrypt(C,s,sk,r,p,q):

    a = C[0]

    d = C[1]

    cp = (dot(a,s,q) + d)%q

    skv = (sk * cp)%q

    skp = number.inverse(sk,p)

    dec = (skp * skv)%p

    return dec



def test(v):

    q = 2**32

    t = 2**16

    m = 74

    w = 86

    n = 13

    b = 16

    #print("Public parameters:",q,n,m,t,w,b)

    s,sk,r,p = skGen(q,n,m,t,w,b)

    PK = pkGen(sk,p,q,s,b,m,n,r)

    C = encrypt(v,PK,p,q,m,n,w)

    D = decrypt(C,s,sk,r,p,q)

    if D != v:

        print("Erro!")

    

for i in range(10000):

    v = randint(0,2**16-1)

    test(v)