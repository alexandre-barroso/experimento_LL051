# Importa o módulo time para manipulação temporal e gerenciamento de delays
import time
# Importa o módulo re, que provê operações avançadas de correspondência de padrões utilizando expressões regulares
import re
# Importa a função build do módulo googleapiclient.discovery, que permite a construção de serviços API RESTful
from googleapiclient.discovery import build
# Importa a classe HttpError do módulo googleapiclient.errors para tratamento de exceções relacionadas a requisições HTTP na API
from googleapiclient.errors import HttpError
# Importa a biblioteca pandas com alias pd, essencial para a manipulação e análise de estruturas de dados tabulares
import pandas as pd
# Importa o módulo json para serialização e desserialização de objetos JSON
import json

# Define a chave do desenvolvedor para autenticação e autorização no uso da API do YouTube
CHAVE_DESENVOLVEDOR = 'SUA_CHAVE_DE_DESENVOLVEDOR'
# Define o nome do serviço da API do YouTube
NOME_SERVICO_YOUTUBE_API = 'youtube'
# Define a versão do serviço da API do YouTube
VERSAO_SERVICO_YOUTUBE_API = 'v3'
# Define o nome do arquivo que armazenará o estado da execução do script, crucial para persistência de dados entre execuções
ARQUIVO_ESTADO = 'estado.json'  # Arquivo para salvar o estado
# Define o nome do arquivo que conterá a lista de URLs dos vídeos a serem processados
ARQUIVO_VIDEOS = 'videos.json'  # Arquivo contendo a lista de URLs de vídeos

# Função responsável por carregar o estado da execução a partir de um arquivo JSON
def carregar_estado():
    try:
        # Abre o arquivo de estado em modo de leitura
        with open(ARQUIVO_ESTADO, 'r') as f:
            # Carrega o conteúdo JSON do arquivo e retorna como um objeto Python
            return json.load(f)
    except FileNotFoundError:
        # Caso o arquivo não exista, retorna um dicionário com valores padrão para continuar a execução
        return {'ultimo_video_processado': None, 'token_pagina': None}

# Função responsável por salvar o estado atual da execução em um arquivo JSON
def salvar_estado(estado):
    # Abre o arquivo de estado em modo de escrita
    with open(ARQUIVO_ESTADO, 'w') as f:
        # Serializa o estado atual em formato JSON e grava no arquivo
        json.dump(estado, f)

# Função que implementa uma espera com contagem regressiva, imprimindo o tempo restante a cada minuto
def aguardar_com_contagem_regressiva(duracao, mensagem="Aguardando..."):
    # Laço de repetição que decrementa a duração em intervalos de 60 segundos
    for restante in range(duracao, 0, -60):
        # Calcula e imprime o tempo restante em horas e minutos
        print(f"{mensagem} {restante//3600} horas {restante%3600//60} minutos restantes.")
        # Suspende a execução do programa por 60 segundos ou o tempo restante, o que for menor
        time.sleep(min(60, restante))

# Função que extrai o ID do vídeo a partir de uma URL do YouTube utilizando expressões regulares
def extrair_id_video_da_url(url):
    # Aplica a expressão regular para encontrar o padrão do ID do vídeo na URL
    correspondencia_id_video = re.match(r'.*(?:youtu.be/|v/|u/\w/|embed/|watch\?v=|&v=)([^#\&\?]*).*', url)
    # Retorna o grupo correspondente ao ID do vídeo se a correspondência for encontrada, caso contrário retorna None
    return correspondencia_id_video.group(1) if correspondencia_id_video else None

# Função que obtém os comentários de um vídeo do YouTube, dado seu ID
def obter_comentarios_video(servico, id_video):
    # Inicializa listas para armazenar os dados dos comentários, datas de publicação, curtidas e títulos dos vídeos
    comentarios, datas, curtidas, titulos_videos = [], [], [], []
    # Carrega o estado atual da execução
    estado = carregar_estado()
    # Define o número máximo de tentativas em caso de erros durante a execução da API
    max_tentativas = 2
    # Inicializa o contador de tentativas
    tentativas = 0
    # Inicializa o contador total de comentários
    total_comentarios = 0  # Inicializa o contador de comentários
    # Laço de repetição que permite até um número máximo de tentativas de execução
    while tentativas <= max_tentativas:
        try:
            # Obtém o título do vídeo utilizando a API do YouTube
            titulo_video = servico.videos().list(part='snippet', id=id_video).execute()['items'][0]['snippet']['title']
            # Obtém os comentários do vídeo utilizando a API do YouTube
            resultados = servico.commentThreads().list(part='snippet', videoId=id_video, textFormat='plainText').execute()

            # Laço de repetição que percorre os resultados dos comentários
            while resultados:
                # Itera sobre cada item nos resultados
                for item in resultados['items']:
                    # Extrai o texto do comentário, data de publicação e contagem de curtidas
                    comentario = item['snippet']['topLevelComment']['snippet']['textDisplay']
                    data = item['snippet']['topLevelComment']['snippet']['publishedAt']
                    curtida = item['snippet']['topLevelComment']['snippet']['likeCount']

                    # Adiciona os dados extraídos às respectivas listas
                    comentarios.append(comentario)
                    datas.append(data)
                    curtidas.append(curtida)
                    titulos_videos.append(titulo_video)
                    # Incrementa o contador total de comentários
                    total_comentarios += 1  # Incrementa o contador de comentários
                    # Imprime a contagem total de comentários extraídos em tempo real
                    print(f"Total de comentários extraídos: {total_comentarios}")  # Imprime a contagem de comentários em tempo real

                # Verifica se há uma próxima página de resultados
                if 'nextPageToken' in resultados:
                    # Obtém a próxima página de resultados utilizando o token da página seguinte
                    resultados = servico.commentThreads().list(part='snippet', videoId=id_video, textFormat='plainText', pageToken=resultados['nextPageToken']).execute()
                else:
                    # Encerra o laço se não houver mais páginas de resultados
                    break
            # Salva o estado atual após a obtenção dos comentários
            salvar_estado({'ultimo_video_processado': id_video, 'token_pagina': None})
            # Retorna um DataFrame pandas contendo os dados dos comentários
            return pd.DataFrame({'Video': titulos_videos, 'Comentario': comentarios, 'Data': datas, 'Curtidas': curtidas})
        except HttpError as e:
            # Verifica se o erro é devido a exceder a cota da API
            if e.resp.status == 403 and 'quota' in str(e):
                # Incrementa o contador de tentativas em caso de erro de cota
                if tentativas < max_tentativas:
                    tentativas += 1
                    # Imprime uma mensagem de erro e aguarda 10 segundos antes de tentar novamente
                    print(f"Erro de cota, tentando novamente ({tentativas}/{max_tentativas})...")
                    time.sleep(10)  # Aguarda 10 segundos antes de tentar novamente
                else:
                    # Imprime uma mensagem e aguarda 25 horas antes de continuar em caso de exceder o número máximo de tentativas
                    print("Cota excedida.")
                    aguardar_com_contagem_regressiva(90000, "Esperando período de cooldown. Aguarde antes de tentar novamente...")
                    # Reseta o contador de tentativas após a espera
                    tentativas = 0  # Reseta as tentativas após a espera
            else:
                # Imprime uma mensagem de erro em caso de outros tipos de exceções da API
                print(f"Erro na API: {e}")
                # Encerra o laço em caso de erro não relacionado à cota
                break

# Função principal que coordena a execução do script
def main():
    # Inicializa o serviço da API do YouTube utilizando as credenciais fornecidas
    servico = build(NOME_SERVICO_YOUTUBE_API, VERSAO_SERVICO_YOUTUBE_API, developerKey=CHAVE_DESENVOLVEDOR)
    # Carrega o estado atual da execução
    estado = carregar_estado()

    # Carrega as URLs dos vídeos a partir do arquivo JSON
    with open(ARQUIVO_VIDEOS, 'r') as f:
        urls_videos = json.load(f)

    # Inicializa um DataFrame pandas para armazenar todos os comentários extraídos
    todos_comentarios = pd.DataFrame()
    # Determina o índice inicial a partir do último vídeo processado, se existir
    indice_inicio = urls_videos.index(estado['ultimo_video_processado']) + 1 if estado['ultimo_video_processado'] in urls_videos else 0

    # Laço de repetição que percorre as URLs dos vídeos a partir do índice inicial
    for url_video in urls_videos[indice_inicio:]:
        # Extrai o ID do vídeo a partir da URL
        id_video = extrair_id_video_da_url(url_video)
        # Verifica se a URL é válida
        if not id_video:
            # Imprime uma mensagem em caso de URL inválida
            print(f"URL inválida: {url_video}")
            continue

        # Imprime uma mensagem indicando o início da extração dos comentários do vídeo
        print(f"Extraindo comentários do vídeo: {url_video}")
        # Obtém os comentários do vídeo e armazena em um DataFrame pandas
        comentarios_df = obter_comentarios_video(servico, id_video)
        # Concatena os novos comentários ao DataFrame existente
        todos_comentarios = pd.concat([todos_comentarios, comentarios_df], ignore_index=True)
        # Imprime uma mensagem indicando que os comentários do vídeo foram extraídos
        print(f"{url_video} extraído!")

    # Salva todos os comentários extraídos em um arquivo CSV
    todos_comentarios.to_csv('corpus.csv', index=False)
    # Imprime uma mensagem indicando que os dados foram salvos
    print("Dados salvos em corpus.csv.")

# Ponto de entrada do script, executa a função principal se o script for executado diretamente
if __name__ == '__main__':
    main()

### Você vai precisar de um arquivo JSON na mesma pasta "videos.json" da seguinte estrutura:
###
### [
    ###"https://www.youtube.com/watch?v=example_video_id1",
    ###"https://www.youtube.com/watch?v=example_video_id2",
    ###"https://www.youtube.com/watch?v=example_video_id3"
###]
