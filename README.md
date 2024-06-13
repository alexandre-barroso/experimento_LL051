# Trabalho final para a disciplina de pós-graduação LL051 (UNICAMP)

Grupo: Alexandre M. Barroso, Lucas Bernardes, Laura Kirasuke.

## Descrição do Processo

O trabalho consiste em uma análise comparativa de comentários do YouTube, visando identificar diferenças linguísticas entre corpora com viés de esquerda e direita. O processo é dividido em várias etapas, descritas brevemente a seguir:

### 1. Coleta de Dados
- **Script:** `scraper.py`
- **Descrição:** Este script é utilizado para baixar comentários do YouTube.
- **Output:** Gera dois arquivos CSV:
  - `corpus_esquerda.csv`: Corpus de comentários de YouTube com viés de esquerda.
  - `corpus_direita.csv`: Corpus de comentários de YouTube com viés de direita.

### 2. Análise dos Dados
- **Script:** `analizador.py`
- **Descrição:** Processa os dados coletados para capturar e analisar diversos elementos.
- **Output:** Gera doze arquivos:
  - `{corpus}_{categoria}.csv`: Arquivo .csv com as instâncias e ocorrências dos elementos analizados.
  - `relatorio_{corpus}_{categoria}.txt`: Relatório da análise do corpus.

### 3. Comparação Estatística
- **Script:** `estatistica.py`
- **Descrição:** Compara os elementos linguísticos apurados nos dois relatórios utilizando o qui-quadrado e o teste de Mann-Whitney.
