import pandas as pd
import matplotlib.pyplot as plt

# Função para carregar os dados do arquivo resultados.txt
def carregar_dados(arquivo):
    try:
        # Lê o arquivo resultados.txt, assumindo o formato CSV com cabeçalho
        dados = pd.read_csv(arquivo)
        return dados
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        return None

# Função para gerar o gráfico de N x Tempo
def gerar_grafico(dados):
    try:
        # Verifica se os dados estão no formato esperado
        if "N" in dados.columns and "Tempo" in dados.columns:
            plt.figure(figsize=(10, 6))
            plt.plot(dados["N"], dados["Tempo"], marker='o', linestyle='-', label="Tempo do Algoritmo")
            plt.xlabel("Tamanho de N")
            plt.ylabel("Tempo (s)")
            plt.title("Relação entre N e o Tempo de Execução do Algoritmo")
            plt.grid(True)
            plt.legend()
            plt.savefig("grafico_N_vs_Tempo.png")  # Salva o gráfico como imagem
            plt.show()
        else:
            print("O arquivo não contém as colunas esperadas: 'N' e 'Tempo'.")
    except Exception as e:
        print(f"Erro ao gerar o gráfico: {e}")

# Caminho do arquivo de resultados
arquivo_resultados = "resultados.txt"

# Carregar os dados e gerar o gráfico
dados = carregar_dados(arquivo_resultados)
if dados is not None:
    gerar_grafico(dados)
