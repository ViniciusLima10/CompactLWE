#include <iostream>
#include <vector>
#include <cstdlib> // Para a função rand()
#include <ctime>   // Para a função time()
#include <numeric> // Para std::gcd
#include <utility>

using namespace std;

// Parâmetros do esquema Compact-LWE (valores fixos para determinismo)
// const int32_t q = 345; // Modulus
// const int n = 6; // Dimension of s
// const int m = 8; // Number of samples in PK
// const int t = 2; // t = p (assumindo t = q / 65536)
// const int w = 2; // Number of samples in encryption
// const int b = 7; // Range of coefficients in ai

const int q = 429496729;  // Exemplo de valor para q
const int n = 13;
const int m = 74;
const int t = 65536;
const int w = 86;
const int b = 16;


// Estrutura para armazenar K e PK
struct PrivateKey {
    vector<int> s; //
    int sk;
    int r;
    int p;
};

struct PublicKey {
    vector<int> ai;
    int pki;
};

struct PublicKeys {
    vector<PublicKey> publicKey;
};

// Função para encontrar inverso modular
int modInverse(int a, int m) {
    int m0 = m, t, q;
    int x0 = 0, x1 = 1;

    if (m == 1)
        return 0;

    while (a > 1) {
        q = a / m;
        t = m;

        m = a % m;
        a = t;
        t = x0;

        x0 = x1 - q * x0;
        x1 = t;
    }

    if (x1 < 0)
        x1 += m0;

    return x1;
}

// Função para gerar um vetor n-dimensional com coordenadas mod q
vector<int> generateVector(int n, int q) {
    vector<int> vec(n);
    for (int i = 0; i < n; ++i) {
        vec[i] = rand() % q; // Atribui um valor aleatório mod q a cada elemento do vetor
    }
    return vec;
}

int gcd(int a, int b) {
    if (b == 0) return a;
    else return gcd(b, a % b);
}

// Função para verificar se três números são coprimos (mútua coprimos)
bool areCoprime(int a, int b, int c) {
    return gcd(a, b) == 1 && gcd(a, c) == 1 && gcd(b, c) == 1;
}

// Função para gerar um valor aleatório ei uniformemente amostrável em anéis de inteiros modulo r
int generateEi(int r) {
    return rand() % r;
}

// Função para calcular o produto interno entre dois vetores
int innerProduct(const vector<int>& a, const vector<int>& b) {
    int result = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        result += a[i] * b[i];
    }
    return result;
}

// Função para calcular sk^-1*q que satisfaz a condição sk * sk^-1*q = -1 mod q
int calculateSkInvQ(int sk) {
    int sk_inv_q = modInverse(sk, q);

    sk_inv_q = (-sk_inv_q) % q;
    if (sk_inv_q < 0)
        sk_inv_q += q;

    return sk_inv_q;
}

// Função para gerar as chaves (Keys) que satisfazem as condições
pair<PrivateKey, PublicKeys> GenerateKeys() {
    PrivateKey privateKey;
    PublicKeys publicKeys;

    cout << "Gerando Chave Privada: " << endl << "(";

    privateKey.s = generateVector(n, q); // Gera o vetor s

    do {
        privateKey.sk = rand() % (q - 1) + 1; // Gera sk entre 1 e q-1
        privateKey.r = rand() % (q - 1) + 1;  // Gera r entre 1 e q-1
        privateKey.p = rand() % (q - 1) + 1;  // Gera p entre 1 e q-1
    } while (!areCoprime(privateKey.sk, privateKey.p, q) || 
             !areCoprime(privateKey.r, privateKey.p, q) || 
             (privateKey.sk * (privateKey.p - 1) + w * privateKey.r * privateKey.p >= q) || 
             (b >= privateKey.r));

    for (int i = 0; i < n; i++) {
        cout << privateKey.s[i] << ", ";
    }
    cout << privateKey.sk << ", " << privateKey.r << ", " << privateKey.p << ")" << endl;

    publicKeys.publicKey.resize(m);

    int k = calculateSkInvQ(privateKey.sk);

    cout << "Gerando Chaves Publicas..." << endl;
    for (int i = 0; i < m; i++) {
        publicKeys.publicKey[i].ai = generateVector(n, b);

        int ei = generateEi(privateKey.r); // gera um erro uniformemente amostrável em mod r
        int inner_product = innerProduct(publicKeys.publicKey[i].ai, privateKey.s);

        publicKeys.publicKey[i].pki = (inner_product + ei * k) % q;
    }

    return make_pair(privateKey, publicKeys); // como faco essa linha??
}

// Function to encrypt the message v
vector<int> Enc(PublicKeys PK, int v) {
    vector<int> c(n + 1); // Initialize the ciphertext vector

    // Sample an integer i uniformly from the set {1, ..., m}
    int i = rand() % m + 1;

    // Get the corresponding sample from PK
    PublicKey sample = PK.publicKey[i - 1]; // Adjust for 0-based indexing

    // Initialize c' with the sample
    vector<int> c_prime = sample.ai;
    int pk_prime = sample.pki;

    // Sample w integers uniformly from the set {1, ..., m}
    for (int j = 0; j < w; j++) {
        int k = rand() % m + 1;
        PublicKey sample_k = PK.publicKey[k - 1]; // Adjust for 0-based indexing

        // Update c' by adding the sample
        for (int l = 0; l < n; l++) {
            c_prime[l] = (c_prime[l] + sample_k.ai[l]) % q;
        }
        pk_prime = (pk_prime + sample_k.pki) % q;
    }

    // Compute c = (a, v - pk mod q)
    for (int l = 0; l < n; l++) {
        c[l] = c_prime[l];
    }
    c[n] = (v - pk_prime) % q;

    return c;
}

int Dec(PrivateKey K, vector<int> c) {
    int c_prime = innerProduct(K.s, vector<int>(c.begin(), c.begin() + n)); // calcula c' = produtoInterno(a, s) mod q
    int skv = (c_prime * K.sk) % q; // calcula skv = sk * c' mod q
    int v = (calculateSkInvQ(K.sk) * skv) % K.p; // calcula v = sk^-1*p * skv mod p
    return v;
}


int main() {
    srand(time(NULL)); // Inicializa a semente aleatória uma vez

    auto keys = GenerateKeys(); // Call the GenerateKeys function

    PrivateKey privateKey = keys.first;
    PublicKeys publicKeys = keys.second;

    for (int i = 0; i < m; i++) {
        cout << "Chave Publica " << i << ": (";
        for (int j = 0; j < n; j++) {
            cout << publicKeys.publicKey[i].ai[j] << ", ";
        }
        cout << publicKeys.publicKey[i].pki << ")" << endl;
    }

    int v = 1;
    cout << "texto plano: " << v << endl;
    vector<int> cypherText = Enc(publicKeys, v);
    cout << "texto cifrado: " << endl;
    for(int i = 0; i < n + 1; i++) {
        cout << cypherText[i] << ", ";
    }

    cout << "Tentativa de decriptacao..." << endl;

    int v_decifrado = Dec(privateKey, cypherText);

    cout<< "texto decifrado: " << v_decifrado << endl;

    return 0;
}