import pandas as pd
import os
import re
from scipy.stats import chi2_contingency, mannwhitneyu

def ler_ocorrencias(arquivo_csv):
    df = pd.read_csv(arquivo_csv)
    total_ocorrencias = df['Ocorrência'].sum()
    instancias_unicas = df['Instância'].nunique()
    frequencias = df['Ocorrência']
    print(f"Lendo {arquivo_csv}: Total Ocorrências = {total_ocorrencias}, Instâncias Únicas = {instancias_unicas}, Frequências = {frequencias.head()}")
    return total_ocorrencias, instancias_unicas, frequencias

def interpretar_resultados(categoria1, categoria2, p_chi2, p_mannwhitney):
    # Definição de "uso"
    # No contexto desta análise, "uso" refere-se a:
    # 1. **Frequência de Ocorrência**: Quantas vezes uma categoria de palavras (por exemplo, emojis, gírias) aparece nos comentários.
    # 2. **Contexto de Uso**: Os tipos de comentários ou situações em que a categoria aparece, indicando o ambiente ou a temática em que as palavras são empregadas.
    # 3. **Distribuição**: A dispersão das ocorrências ao longo dos comentários, observando se a categoria é usada de maneira uniforme ou se está concentrada em certos trechos.
    # 4. **Variedade de Instâncias**: A diversidade de palavras ou expressões dentro de uma categoria, indicando a riqueza de vocabulário utilizado.

    if categoria1 == categoria2:
        if p_chi2 < 0.05 and p_mannwhitney < 0.05:
            return (f"Existe uma diferença estatisticamente significativa na comparação de {categoria1} entre os dois corpora, tanto na frequência quanto na distribuição das ocorrências. "
                    f"Isso indica que a maneira e a frequência com que {categoria1} são usados diferem substancialmente entre os dois corpora. "
                    f"O teste Qui-Quadrado mostra que a associação entre {categoria1} e o corpus é forte, sugerindo que a ocorrência de {categoria1} está relacionada de maneira diferente em cada corpus. "
                    f"Já o teste Mann-Whitney U revela que a distribuição das frequências de {categoria1} é significativamente diferente entre os dois corpora, indicando variações na quantidade de uso em diferentes contextos ou situações.")
        elif p_chi2 < 0.05 and p_mannwhitney >= 0.05:
            return (f"Existe uma diferença estatisticamente significativa na comparação de {categoria1} entre os dois corpora na variação das ocorrências, mas as distribuições das frequências são semelhantes. "
                    f"Isso sugere que, apesar das diferenças nos contextos de uso de {categoria1}, a quantidade total de ocorrências é similar em ambos os corpora. "
                    f"O teste Qui-Quadrado indica que a presença de {categoria1} está associada de maneira diferente nos dois corpora, enquanto o teste Mann-Whitney U mostra que as distribuições de frequência não são significativamente diferentes, indicando que a quantidade de uso de {categoria1} é similar.")
        elif p_chi2 >= 0.05 and p_mannwhitney < 0.05:
            return (f"As distribuições das frequências de {categoria1} entre os dois corpora são significativamente diferentes, mas o padrão geral de uso não mostra uma diferença clara. "
                    f"O teste Mann-Whitney U sugere que {categoria1} é usado com frequências diferentes nos dois corpora, enquanto o teste Qui-Quadrado não indica uma forte associação entre {categoria1} e o corpus. "
                    f"Isso implica que, embora a quantidade de {categoria1} usada nos comentários seja diferente, os contextos ou padrões de uso são consistentes.")
        elif p_chi2 >= 0.05 and p_mannwhitney >= 0.05:
            return (f"Não existe uma diferença estatisticamente significativa na comparação de {categoria1} entre os dois corpora, tanto na frequência quanto na distribuição das ocorrências. "
                    f"O teste Qui-Quadrado e o teste Mann-Whitney U não encontraram diferenças significativas, indicando que {categoria1} é usado de maneira semelhante em termos de frequência e contexto em ambos os corpora.")
        else:
            return (f"Os resultados indicam uma possível diferença na comparação de {categoria1} entre os dois corpora, tanto na frequência quanto na distribuição das ocorrências, mas não são conclusivos. "
                    f"Pode haver uma diferença, mas os dados não são suficientemente fortes para confirmar isso.")

    else:
        if p_chi2 < 0.05 and p_mannwhitney < 0.05:
            return (f"Existe uma diferença estatisticamente significativa entre as categorias {categoria1} e {categoria2}, tanto na frequência quanto na distribuição das ocorrências. "
                    f"O teste Qui-Quadrado indica que a associação entre as categorias {categoria1} e {categoria2} é significativa, sugerindo que a ocorrência de uma categoria não é independente da outra. "
                    f"O teste Mann-Whitney U mostra que a distribuição das frequências de {categoria1} e {categoria2} são significativamente diferentes, indicando que uma categoria é usada com mais frequência ou em diferentes contextos que a outra.")
        elif p_chi2 < 0.05 and p_mannwhitney >= 0.05:
            return (f"Existe uma diferença estatisticamente significativa na associação entre as categorias {categoria1} e {categoria2}, mas as distribuições das frequências são semelhantes. "
                    f"O teste Qui-Quadrado sugere que {categoria1} e {categoria2} não são usadas de forma independente uma da outra, enquanto o teste Mann-Whitney U indica que a quantidade de uso é similar em termos de frequência. "
                    f"Isso pode significar que ambas aparecem frequentemente nos mesmos contextos, mas não necessariamente na mesma quantidade.")
        elif p_chi2 >= 0.05 and p_mannwhitney < 0.05:
            return (f"As distribuições das frequências das categorias {categoria1} e {categoria2} são significativamente diferentes, mas não há uma forte associação entre elas. "
                    f"O teste Mann-Whitney U mostra que a frequência de uso é diferente para {categoria1} e {categoria2}, indicando padrões distintos de uso, enquanto o teste Qui-Quadrado não encontrou uma associação significativa entre as categorias.")
        elif p_chi2 >= 0.05 and p_mannwhitney >= 0.05:
            return (f"Não existe uma diferença estatisticamente significativa entre as categorias {categoria1} e {categoria2}, tanto na frequência quanto na distribuição das ocorrências. "
                    f"Os testes Qui-Quadrado e Mann-Whitney U sugerem que {categoria1} e {categoria2} são usados de maneira semelhante, sem diferenças notáveis na quantidade de uso ou nos contextos em que aparecem.")
        else:
            return (f"Os resultados indicam uma possível diferença entre as categorias {categoria1} e {categoria2}, tanto na frequência quanto na distribuição das ocorrências, mas não são conclusivos. "
                    f"Pode haver uma diferença, mas os dados não são suficientemente fortes para confirmar isso.")


def analisar_estatisticas(categorias, arquivos_corpus):
    relatorios = {}

    # Ler os relatórios para cada categoria e corpus
    for arquivo in arquivos_corpus:
        corpus = os.path.splitext(arquivo)[0]
        relatorios[corpus] = {}
        for categoria in categorias.keys():
            arquivo_csv = f'{corpus}_{categoria}.csv'
            total_ocorrencias, instancias_unicas, frequencias = ler_ocorrencias(arquivo_csv)
            relatorios[corpus][categoria] = {
                'total_ocorrencias': total_ocorrencias,
                'instancias_unicas': instancias_unicas,
                'frequencias': frequencias
            }

    with open('relatorio_final.txt', 'w') as relatorio_final:
        relatorio_final.write('Relatório Estatístico Final\n\n')
        relatorio_final.write('### Explicação dos Testes ###\n')
        relatorio_final.write('**Teste Qui-Quadrado**:\n')
        relatorio_final.write('O que mede: O teste Qui-Quadrado de independência mede a associação entre duas variáveis categóricas. No contexto dos corpora, ele verifica se a distribuição das ocorrências de duas categorias (por exemplo, emojis vs. gírias) é independente uma da outra.\n')
        relatorio_final.write('Interpretação: Um p-value significativo (geralmente p < 0.05) sugere que as duas categorias não são independentes, ou seja, a ocorrência de uma categoria pode estar associada à ocorrência da outra.\n\n')
        relatorio_final.write('**Teste Mann-Whitney U**:\n')
        relatorio_final.write('O que mede: O teste Mann-Whitney U compara duas amostras independentes para determinar se suas distribuições diferem significativamente. No contexto dos corpora, ele compara as frequências das ocorrências das categorias para ver se uma é significativamente maior ou menor do que a outra.\n')
        relatorio_final.write('Interpretação: Um p-value significativo (geralmente p < 0.05) sugere que as distribuições das frequências das duas categorias são significativamente diferentes.\n\n')

        # Análise intra-corpus
        for corpus in relatorios.keys():
            relatorio_final.write(f'\n\n\n#### Análise intra-corpus para {corpus}:\n')
            categorias_corpus = list(relatorios[corpus].keys())
            for i, cat1 in enumerate(categorias_corpus):
                for cat2 in categorias_corpus[i + 1:]:
                    dados1 = relatorios[corpus][cat1]
                    dados2 = relatorios[corpus][cat2]

                    # Teste qui-quadrado para independência
                    table = [[dados1['total_ocorrencias'], dados1['instancias_unicas']],
                             [dados2['total_ocorrencias'], dados2['instancias_unicas']]]
                    chi2, p_chi2, _, _ = chi2_contingency(table)

                    # Teste Mann-Whitney U
                    u_stat, p_mannwhitney = mannwhitneyu(dados1['frequencias'], dados2['frequencias'], alternative='two-sided')

                    interpretacao = interpretar_resultados(cat1, cat2, p_chi2, p_mannwhitney)

                    relatorio_final.write(f'\nComparação entre {cat1} e {cat2}:\n')
                    relatorio_final.write(f'Teste qui-quadrado: chi2 = {chi2:.4f}, p-value = {p_chi2:.4f} ({p_chi2:.4e})\n')
                    relatorio_final.write(f'Teste Mann-Whitney U: U = {u_stat:.4f}, p-value = {p_mannwhitney:.4f} ({p_mannwhitney:.4e})\n')
                    relatorio_final.write(f'# INTERPRETAÇÃO: {interpretacao}\n')

        # Análise inter-corpus para cada categoria
        categorias_lista = list(categorias.keys())
        relatorio_final.write(f'\n\n\n#### Análise entre corpora:\n')
        for categoria in categorias_lista:
            corpus1, corpus2 = list(relatorios.keys())
            dados_corpus1 = relatorios[corpus1][categoria]
            dados_corpus2 = relatorios[corpus2][categoria]

            # Teste qui-quadrado para independência
            table = [[dados_corpus1['total_ocorrencias'], dados_corpus1['instancias_unicas']],
                     [dados_corpus2['total_ocorrencias'], dados_corpus2['instancias_unicas']]]
            chi2, p_chi2, _, _ = chi2_contingency(table)

            # Teste Mann-Whitney U
            u_stat, p_mannwhitney = mannwhitneyu(dados_corpus1['frequencias'], dados_corpus2['frequencias'], alternative='two-sided')

            interpretacao = interpretar_resultados(categoria, categoria, p_chi2, p_mannwhitney)

            relatorio_final.write(f'\n\nAnálise inter-corpus para a categoria {categoria}:\n')
            relatorio_final.write(f'Teste qui-quadrado: chi2 = {chi2:.4f}, p-value = {p_chi2:.4f} ({p_chi2:.4e})\n')
            relatorio_final.write(f'Teste Mann-Whitney U: U = {u_stat:.4f}, p-value = {p_mannwhitney:.4f} ({p_mannwhitney:.4e})\n')
            relatorio_final.write(f'# INTERPRETAÇÃO: {interpretacao}\n')


if __name__ == "__main__":
    # Lista de arquivos de corpus a serem processados
    arquivos_corpus = ['corpus_direita.csv', 'corpus_esquerda.csv']

    # Definição dos padrões regex para as categorias (manter igual com o analisador.py)
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
        'Abreviações': re.compile(r'\b(adm|adms|admns|amg|amgs|amigo|aq|aqi|aki|bj|bjs|blz|blzs|bo|boa|bom|cap|caps|cm|cms|cmg|cmgs|ctz|ctzs|dms|dmr|dmais|dnv|dnov|doq|dq|dps|dp|dr|drs|f1|fdp|fdps|fds|fimds|fmz|fmzs|flw|flws|fzr|fzrs|glr|glrs|gnt|gnts|hj|hoj|kd|kde|mds|mlk|mlke|mlqs|mlhr|msg|msgs|msm|msms|mt|mts|mto|mta|mtas|mtos|n|nao|nd|nada|ngc|ngm|ningm|nn|non|obg|obgd|oq|oqe|p|pd|pdc|pdcs|pdp|pdps|pft|pfts|pfv|pfvs|plmdds|pmds|pprt|pprts|pq|pqps|psé|pv|pvc|q|qd|qdo|qt|qts|rlx|rlxa|rt|rts|s|sd|sdd|sdds|sla|slc|slk|sm|sma|sqn|ss|t|tb|tbm|td|tds|tlgd|tlgs|tmj|tnc|tnd|trd|trds|tt|tts|vc|vcs|v6|vdd|vdds|vsf|vlw|vtnc|yt|ytb|zap|zaps)\b', flags=re.IGNORECASE),
        'Ênclise e Mesóclise': re.compile(r'\b(\w*(?:-a|-á|-ás|-as|-o|-lá|-lo|-los|-na|-nas|-no|-nos|-ia|-ias|-se|-te|-me|-lhe|-lhes|-ei|-emos|-ão|-íamos|-iam|-íeis|-eis|-vos|-os))\b', flags=re.IGNORECASE)
    }

    # Chamar a função de análise estatística
    analisar_estatisticas(categorias, arquivos_corpus)
