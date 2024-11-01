#include <iostream>
#include <vector>
#include <cstdlib>
#include <cmath>
#include <ctime>
#include <tuple>

using namespace std;

// Função para calcular o inverso modular usando o Algoritmo Estendido de Euclides
int modular_inverse(int a, int m) {
    int m0 = m, x0 = 0, x1 = 1;
    if (m == 1) return 0;
    while (a > 1) {
        int q = a / m;
        int t = m;
        m = a % m;
        a = t;
        t = x0;
        x0 = x1 - q * x0;
        x1 = t;
    }
    if (x1 < 0) x1 += m0;
    return x1;
}

// Função gcd (Máximo Divisor Comum)
int gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

// Função de soma de vetores com módulo q
vector<int> vecsum(const vector<int>& a, const vector<int>& b, int q) {
    int n = a.size();
    vector<int> c(n);
    for (int i = 0; i < n; i++) {
        c[i] = (a[i] + b[i]) % q;
    }
    return c;
}

// Função de produto escalar com módulo q
int dot(const vector<int>& a, const vector<int>& b, int q) {
    int s = 0;
    for (int i = 0; i < a.size(); i++) {
        s = (s + a[i] * b[i]) % q;
    }
    return s;
}

// Gera um vetor aleatório de tamanho n com elementos no intervalo [0, q-1]
vector<int> genVector(int n, int q) {
    vector<int> v(n);
    for (int i = 0; i < n; i++) {
        v[i] = rand() % q;
    }
    return v;
}

// Função para gerar as chaves secretas com as condições matemáticas especificadas
tuple<vector<int>, int, int, int> skGen(int q, int n, int m, int t, int w, int b) {
    vector<int> s;
    int sk, r, p;
    while (true) {
        s = genVector(n, q);
        
        // Gera r com verificação para garantir que não seja zero
        do {
            r = rand() % (2 * b) + b + 1;
        } while (r == 0);
        cout << "Valor de r gerado: " << r << endl;

        // Gera sk e garante que gcd(sk, q) seja 1 e sk != 0
        do {
            sk = rand() % (q / (2 * (t - 1)) - 1) + 2;
        } while (gcd(sk, q) != 1 || sk == 0);
        cout << "Valor de sk gerado: " << sk << endl;
        
        // Gera p e verifica que gcd(p, sk) == 1 e gcd(p, q) == 1 e p != 0
        do {
            p = rand() % (q / (2 * w * r) - 1 + t) + t;
        } while ((gcd(p, sk) != 1 || gcd(p, q) != 1 || p == 0));
        cout << "Valor de p gerado: " << p << endl;

        if (t <= p && gcd(p, q) == 1 && gcd(p, sk) == 1 && gcd(q, sk) == 1 &&
            sk * (t - 1) + w * r * p < q && b < r && r < q && sk < q && p < q) {
            cout << "Condições válidas para s, sk, r, p.\n";
            break;
        }
    }
    return make_tuple(s, sk, r, p);
}

// Função para gerar a chave pública com base na chave secreta
vector<pair<vector<int>, int>> pkGen(int sk, int p, int q, const vector<int>& s, int b, int m, int n, int r) {
    vector<pair<vector<int>, int>> PK;
    for (int i = 0; i < m; i++) {
        vector<int> a = genVector(n, b);
        int e = rand() % (r - 1) + 1;
        int skq = modular_inverse(sk, q);
        cout << "Inverso modular skq: " << skq << endl;
        int pk = (dot(a, s, q) + e * skq * p) % q;
        PK.push_back(make_pair(a, pk));
    }
    return PK;
}

// Função de encriptação
pair<vector<int>, int> encrypt(int v, const vector<pair<vector<int>, int>>& PK, int p, int q, int m, int n, int w) {
    vector<int> C0(n, 0);
    int C1 = 0;
    for (int j = 0; j < w; j++) {
        int i = rand() % m;
        C0 = vecsum(C0, PK[i].first, q);
        C1 = (C1 + PK[i].second) % q;
    }
    C1 = (v - C1) % q;
    return make_pair(C0, C1);
}

// Função de descriptografia
int decrypt(const pair<vector<int>, int>& C, const vector<int>& s, int sk, int r, int p, int q) {
    const vector<int>& a = C.first;
    int d = C.second;
    int cp = (dot(a, s, q) + d) % q;
    int skv = (sk * cp) % q;
    int skp = modular_inverse(sk, p);
    cout << "Valor de skp (inverso modular): " << skp << endl;
    return (skp * skv) % p;
}

// Função de teste
void test(int v) {
    long long q = (1LL << 32);  // Utilizando long long para representar 2^32
    int t = 1 << 16;
    int m = 74;
    int w = 86;
    int n = 13;
    int b = 16;

    vector<int> s;
    int sk, r, p;
    tie(s, sk, r, p) = skGen(q, n, m, t, w, b);  // Atribuindo valores de retorno da tupla
    auto PK = pkGen(sk, p, q, s, b, m, n, r);
    auto C = encrypt(v, PK, p, q, m, n, w);
    int D = decrypt(C, s, sk, r, p, q);

    if (D != v) {
        cout << "Erro na decodificação!" << endl;
    } else {
        cout << "Sucesso na decodificação!" << endl;
    }
}

int main() {
    srand(time(0));  // Seed para números aleatórios
    for (int i = 0; i < 10; i++) {  // Teste com 10 iterações
        int v = rand() % ((1 << 16) - 1);
        test(v);
    }
    return 0;
}
