import pandas as pd

# Função para carregar o CSV de forma robusta
def carregar_csv_robusto(caminho_arquivo):
    try:
        # Carregar o arquivo CSV ignorando linhas problemáticas e usando o engine 'python' para maior robustez
        df = pd.read_csv(caminho_arquivo, delimiter=',', on_bad_lines='skip', engine='python', quoting=3)
        return df
    except Exception as e:
        # Em caso de erro, exibir a mensagem de erro e retornar None
        print(f"Erro ao carregar {caminho_arquivo}: {e}")
        return None

# Função para limitar o número de comentários em um DataFrame
def limitar_comentarios(df, max_comentarios=100000):
    # Contar o número de comentários no DataFrame
    num_comentarios = len(df)

    # Se o número de comentários for maior que o limite máximo permitido
    if num_comentarios > max_comentarios:
        # Truncar o DataFrame para ter apenas o número máximo de comentários permitidos
        df = df.iloc[:max_comentarios]
        print(f"Corpus truncado para {max_comentarios} comentários.")
    else:
        # Caso contrário, informar que o corpus não foi truncado
        print(f"Corpus tem {num_comentarios} comentários e não foi truncado.")

    return df

# Função para salvar o DataFrame em um arquivo CSV
def salvar_csv(df, caminho_arquivo):
    # Salvar o DataFrame no arquivo CSV especificado
    df.to_csv(caminho_arquivo, index=False)
    print(f"Dados salvos em {caminho_arquivo}")

# Caminhos dos arquivos CSV a serem processados
arquivos_csv = {
    'direita': 'corpus_direita.csv',
    'esquerda': 'corpus_esquerda.csv'
}

# Laço para carregar e processar cada arquivo CSV
for lado, caminho in arquivos_csv.items():
    print(f"Processando {caminho}...")
    # Carregar o CSV de forma robusta
    df = carregar_csv_robusto(caminho)

    # Se o DataFrame foi carregado corretamente
    if df is not None:
        # Limitar o número de comentários no DataFrame
        df_limitado = limitar_comentarios(df)
        # Salvar o DataFrame processado de volta no arquivo CSV
        salvar_csv(df_limitado, caminho)
