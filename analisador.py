import pandas as pd
import re
import os
from tqdm import tqdm
from multiprocessing import Pool

# Função para preprocessar o texto dos comentários
def preprocessar_comentario(texto):
    # Remove URLs
    texto = re.sub(r'https?://\S+|www\.\S+', '', texto)
    # Remove pontuações e caracteres especiais
    texto = re.sub(r'[!\"#$%&\'()*+,\./:;<=>?@\[\\\]^_`{|}~]+', ' ', texto)
    # Remove espaços em excesso
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

# Função para contar o número de palavras no texto
def contar_palavras(texto):
    if pd.isna(texto):
        return 0
    palavras = re.findall(r'\b\w+\b', str(texto))
    return len(palavras)

# Função para contar ocorrências de um padrão regex no texto
def encontrar_ocorrencias(texto, padrao):
    if not isinstance(texto, str):
        return []
    return padrao.findall(texto)

def salvar_ocorrencias(df, categoria, padrao, saida_csv, total_palavras):
    tqdm.pandas(desc=f"Processando {categoria}")
    # Encontra todas as ocorrências e expande em linhas individuais
    todas_ocorrencias = df['Comentario'].apply(lambda x: encontrar_ocorrencias(x, padrao)).explode()

    # Filtra ocorrências vazias
    todas_ocorrencias = todas_ocorrencias[todas_ocorrencias.notnull()]

    # Normaliza todas as ocorrências para minúsculas
    todas_ocorrencias = todas_ocorrencias.str.lower()

    # Usamos um contador para contar cada ocorrência individualmente
    contagem_ocorrencias = {}
    resultados = []

    for ocorrencia in todas_ocorrencias:
        if ocorrencia in contagem_ocorrencias:
            contagem_ocorrencias[ocorrencia] += 1
        else:
            contagem_ocorrencias[ocorrencia] = 1
        resultados.append((ocorrencia, contagem_ocorrencias[ocorrencia]))

    # Convertendo resultados para um DataFrame
    resultados_df = pd.DataFrame(resultados, columns=['Instância', 'Ocorrência'])
    resultados_df = unir_instancias(resultados_df)
    resultados_df.to_csv(saida_csv, index=False)

def unir_instancias(df):
    # Agrupa por instância e soma as ocorrências
    df = df.groupby('Instância', as_index=False)['Ocorrência'].sum()
    return df

def processar_categoria(args):
    # Desempacota a lista 'args' em cinco variáveis separadas
    df, categoria, padrao, saida_csv, total_palavras = args
    # Chama a função salvar_ocorrencias, que processa os dados e salva os resultados
    salvar_ocorrencias(df, categoria, padrao, saida_csv, total_palavras)

# Função para analisar ocorrências e gerar um relatório em texto
def analisar_ocorrencias(categoria, arquivo_csv, saida_txt, total_palavras):
    # Carrega o arquivo CSV em um DataFrame
    df_analise = pd.read_csv(arquivo_csv)

    # Calcula o total de ocorrências
    total_ocorrencias = df_analise['Ocorrência'].sum()

    # Verifica se total_palavras é zero para evitar divisão por zero
    if total_palavras == 0:
        frequencia = 0
    else:
        # Calcula a frequência por 1000 palavras
        frequencia = (total_ocorrencias / total_palavras) * 1000

    # Número de instâncias únicas
    instancias_unicas = df_analise['Instância'].nunique()

    # Verifica se o DataFrame está vazio para evitar erro na obtenção da instância mais frequente
    if df_analise.empty:
        instancia_mais_frequente = "N/A"
        contagem_instancia_mais_frequente = 0
    else:
        # Instância mais frequente e sua contagem
        instancia_mais_frequente = df_analise.loc[df_analise['Ocorrência'].idxmax()]['Instância']
        contagem_instancia_mais_frequente = df_analise['Ocorrência'].max()

    # Escreve o relatório em um arquivo de texto
    with open(saida_txt, 'w') as arquivo:
        arquivo.write(f'Resumo de {categoria} no arquivo {os.path.basename(arquivo_csv)}:\n\n')
        arquivo.write(f'Número de instâncias únicas: {instancias_unicas}\n')
        arquivo.write(f'Total de ocorrências: {total_ocorrencias}\n')
        arquivo.write(f'Instância mais frequente: {instancia_mais_frequente}\n')
        arquivo.write(f'Contagem da instância mais frequente: {contagem_instancia_mais_frequente}\n')
        arquivo.write(f'Frequência de {categoria} a cada 1000 palavras: {frequencia:.2f}\n')

# Definição dos padrões regex para as categorias
categorias = {
    'Emojis': re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F700-\U0001F77F"
        u"\U0001F780-\U0001F7FF"
        u"\U0001F800-\U0001F8FF"
        u"\U0001F900-\U0001F9FF"
        u"\U0001FA00-\U0001FA6F"
        u"\U0001FA70-\U0001FAFF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE),
    'Contrações': re.compile(r'\b(bora|cum|cuma|cumas|cuns|dum|duma|dumas|duns|fazemo|fizemo|fomo|né|num|numa|numas|nuns|ouvimo|pra|pras|pro|pros|tá|tamo|tava|tô|vamo|vimo|num|numa|numas|numca|pro|pros|pra|pras|ta|to|tou|vamo|vamu|vamu|vimo|vamu)\b', flags=re.IGNORECASE),
    'Gírias': re.compile(r'\b(cringe|cringey|exposed|exp|fake|feke|fak|gado|gad|hype|hyp|lacrar|lacrei|lacrou|lacraste|lacrando|lacra|lacrante|lacração|mitar|mitou|mitando|mito|mitos|ranço|ranços|show|showzaço|showzão|tanka|tankei|tanko|tankaria|tankou|tankando|top|topzera|topzeira|topper|treta|tretas|zoar|zoei|zoa|zoas|zoou|zoando|zoado|zoada|zoeira|role|rolê|roles|rolezinho|chapado|chapada|suave|sussa|susse|paia|pampa|massa|irado|barato|balacobaco|maneiro|daora|da hora|demais|zica|brisa|brisado|brisada|fita|zueira|zueiro|firmeza|firmeza|massa|sussa|belê|belza|véio|véi|véia|véias|mano|manos|mina|minas|migo|miga|brother|brow|sister|sis|cabra|cabrona|bicho|truta|pivete|vacilão|vacilona|vacilou|bolado|bolada|topado|topada|saidêra|zoado|brab|bafômetro|copo sujo|porre|perrengue|trampo|corre|breja|brejas|chop|chopada|bebedeira|manguaça|goró|caixote|caixotado|bico|falsiane|chapisco|serolado|pegada|mandinga|caô|caraio|cascata|cracudo|bafafá|baita|batidão|batida|papagaio|popozuda|ralado|ralada|mala|embatucado|marimba|zé ruela|zigoto|juntado|lombra|lombrar|macumbeiro|mago|batera|miliano|moscando|naba|tá ligado|pá|pego na curva|pé rapado|pelamô|pelego|pindaíba|pistolão|poita|presepada|quebrado|quebra pau|quicar|quitute|ralé|ralo|ramela|ranzinza|resenha|safado|safada|se achar|serumano|seu mano|treta|tiltado|tiltada|tirar onda|tirar um sarro|topado|trampo|tranquilo|vacilão|vaza|vazado|vazando|vaza|vela|zoação|zerado|zica|zicado|zoado|zoação|zoeiro|zona|zoneiro)\b', flags=re.IGNORECASE),
    'Xingamentos': re.compile(r'\b(arrombada|arrombado|babaca|babacas|bosta|bostas|cacete|cacetes|caraio|caraia|caraios|caralho|caralhos|cagão|cagona|cagonas|cagões|canalha|canalhas|cu|cus|cuzão|cuzona|cuzonas|cuzões|escrota|escrotas|escroto|escrotos|estúpida|estúpidas|estúpido|estúpidos|filha da puta|filhas da puta|filho da puta|filhos da puta|foda|foder|fodida|fodidas|fodido|fodidos|idiota|idiotas|imbecil|imbecis|kralho|krl|lixo|lixos|merda|m3rda|merd@|merdas|mongoloide|mongoloides|otária|otárias|otário|otários|pica|picas|pilantra|pilantras|piranha|piranhas|poha|porra|porras|putaria|putarias|retardada|retardadas|retardado|retardados|safada|safadas|safado|safados|trouxa|trouxas|vadia|vadias|vagabunda|vagabundas|vagabundo|vagabundos)\b', flags=re.IGNORECASE),
    'Abreviações': re.compile(r'\b(adm|adms|admns|amg|amgs|aq|aqi|aki|bj|bjs|blz|blzs|cap|caps|cm|cms|cmg|cmgs|ctz|ctzs|dms|dmr|dmais|dnv|dnov|doq|dq|dps|dp|dr|drs|f1|fdp|fdps|fds|fimds|fmz|fmzs|flw|flws|fzr|fzrs|glr|glrs|gnt|gnts|hj|hoj|kd|kde|mds|mlk|mlke|mlqs|mlhr|msg|msgs|msm|msms|mt|mts|mto|mta|mtas|mtos|n|nao|nd|nada|ngc|ngm|ningm|nn|non|obg|obgd|oq|oqe|p|pd|pdc|pdcs|pdp|pdps|pft|pfts|pfv|pfvs|plmdds|pmds|pprt|pprts|pq|pqps|psé|pv|pvc|q|qd|qdo|qt|qts|rlx|rlxa|rt|rts|s|sd|sdd|sdds|sla|slc|slk|sm|sma|sqn|ss|t|tb|tbm|td|tds|tlgd|tlgs|tmj|tnc|tnd|trd|trds|tt|tts|vc|vcs|v6|vdd|vdds|vsf|vlw|vtnc|yt|ytb|zap|zaps)\b', flags=re.IGNORECASE),
    'Ênclise e Mesóclise': re.compile(r'\b(\w*(?:-a|-á|-ás|-as|-o|-lá|-lo|-los|-na|-nas|-no|-nos|-ia|-ias|-se|-te|-me|-lhe|-lhes|-ei|-emos|-ão|-íamos|-iam|-íeis|-eis|-vos|-os))\b', flags=re.IGNORECASE)
}

# Função principal que coordena a execução do script
if __name__ == "__main__":
    # Lista de arquivos de corpus a serem processados
    arquivos_corpus = ['corpus_direita.csv', 'corpus_esquerda.csv']

    # Cria um pool de processos para executar tarefas em paralelo
    pool = Pool(processes=4)

    # Itera sobre cada arquivo na lista de arquivos de corpus
    for arquivo in arquivos_corpus:
        # Calcula o total de palavras no corpus
        total_palavras = 0
        for df_chunk in pd.read_csv(arquivo, chunksize=50000):
            total_palavras += df_chunk['Comentario'].apply(contar_palavras).sum()

        # Lê cada arquivo em partes (cada parte contendo até 5000 linhas)
        for df_chunk in pd.read_csv(arquivo, chunksize=50000):
            # Prepara uma lista de tarefas, onde cada tarefa é uma tupla contendo:
            # (parte dos dados, categoria, padrão regex, nome do arquivo de saída)
            tasks = [(df_chunk, cat, pat, f'{os.path.splitext(arquivo)[0]}_{cat}.csv', total_palavras) for cat, pat in categorias.items()]
            # Distribui as tarefas para serem processadas pelo pool de processos
            pool.map(processar_categoria, tasks)

    # Fecha o pool de processos e espera que todas as tarefas terminem
    pool.close()
    pool.join()

    # Análise de ocorrências e geração de relatórios
    for arquivo in arquivos_corpus:
        for categoria in categorias.keys():
            arquivo_csv = f'{os.path.splitext(arquivo)[0]}_{categoria}.csv'
            saida_txt = f'relatorio_{os.path.splitext(arquivo)[0]}_{categoria}.txt'
            analisar_ocorrencias(categoria, arquivo_csv, saida_txt, total_palavras)
