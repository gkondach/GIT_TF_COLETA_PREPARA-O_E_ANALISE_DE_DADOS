#!/usr/bin/env python3
# 02_analise.py
# Script responsável por ler a base limpa e gerar estatísticas/plots
# Entrada: /mnt/data/orgaos_analysis_outputs/orgaos_deputados_limpo.csv
# Saídas: diversos CSVs e PNGs na mesma pasta

import os, pandas as pd, matplotlib.pyplot as plt

INPUT_CSV = "/mnt/data/orgaos_analysis_outputs/orgaos_deputados_limpo.csv"
OUTPUT_DIR = "/mnt/data/orgaos_analysis_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def carregar(path=INPUT_CSV):
    if not os.path.exists(path):
        raise FileNotFoundError("Arquivo limpo não encontrado: " + path)
    df = pd.read_csv(path, sep=";", encoding="utf-8", low_memory=False, parse_dates=["dataInicio","dataFim"])
    return df

def gerar_tabelas(df):
    orgs_por_deputado = df.groupby(["nomeDeputado","legislatura"]).size().reset_index(name="qtd_orgaos")
    orgs_por_deputado.to_csv(os.path.join(OUTPUT_DIR, "orgaos_por_deputado.csv"), index=False, sep=";")

    part_counts = df.groupby(["siglaPartido","nomeDeputado"]).size().reset_index(name="qtd")
    media_partido = part_counts.groupby("siglaPartido")["qtd"].mean().reset_index(name="media_participacoes_por_deputado")
    media_partido.to_csv(os.path.join(OUTPUT_DIR, "media_partido.csv"), index=False, sep=";")

    orgs_populares = df.groupby("nomeOrgao")["nomeDeputado"].nunique().reset_index(name="num_deputados").sort_values(by="num_deputados", ascending=False)
    orgs_populares.to_csv(os.path.join(OUTPUT_DIR, "orgaos_populares.csv"), index=False, sep=";")

    participacoes_leg = df["legislatura"].value_counts().sort_index().reset_index()
    participacoes_leg.columns = ["legislatura","qtd_participacoes"]
    participacoes_leg.to_csv(os.path.join(OUTPUT_DIR, "participacoes_por_legislatura.csv"), index=False, sep=";")

    uf_counts = df.groupby("siglaUF")["nomeDeputado"].nunique().reset_index(name="num_deputados").sort_values(by="num_deputados", ascending=False)
    uf_counts.to_csv(os.path.join(OUTPUT_DIR, "participacao_por_uf.csv"), index=False, sep=";")

    return {
        "orgaos_por_deputado": orgs_por_deputado,
        "media_partido": media_partido,
        "orgaos_populares": orgs_populares,
        "participacoes_leg": participacoes_leg,
        "uf_counts": uf_counts
    }

def gerar_graficos(df, stats):
    # Top 10 deputados por participações
    top_deputados = df.groupby("nomeDeputado").size().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10,6))
    top_deputados.plot(kind="barh")
    plt.gca().invert_yaxis()
    plt.title("Top 10 Deputados com Mais Participações em Órgãos")
    plt.xlabel("Quantidade de Participações")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top10_deputados.png"))
    plt.close()

    # Top 10 órgãos por número de deputados distintos
    top_orgaos = stats["orgaos_populares"].head(10).set_index("nomeOrgao")["num_deputados"].sort_values(ascending=True)
    plt.figure(figsize=(10,6))
    top_orgaos.plot(kind="barh")
    plt.title("Top 10 Órgãos por Número de Deputados Distintos")
    plt.xlabel("Número de Deputados")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top10_orgaos.png"))
    plt.close()

    # Participações por legislatura
    part_leg = stats["participacoes_leg"].set_index("legislatura")["qtd_participacoes"]
    plt.figure(figsize=(8,5))
    part_leg.plot(kind="line", marker="o")
    plt.title("Participações Registradas por Legislatura")
    plt.xlabel("Legislatura")
    plt.ylabel("Quantidade de Participações")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "participacoes_por_legislatura.png"))
    plt.close()

    # Top 10 partidos por média de participações por deputado
    top_partidos = stats["media_partido"].sort_values(by="media_participacoes_por_deputado", ascending=False).head(10).set_index("siglaPartido")["media_participacoes_por_deputado"]
    plt.figure(figsize=(10,6))
    top_partidos.plot(kind="bar")
    plt.title("Top 10 Partidos por Média de Participações por Deputado")
    plt.xlabel("Partido")
    plt.ylabel("Média de Participações por Deputado")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top10_partidos_media.png"))
    plt.close()

    # Top 10 UFs por número de deputados
    top_ufs = stats["uf_counts"].head(10).set_index("siglaUF")["num_deputados"]
    plt.figure(figsize=(10,6))
    top_ufs.plot(kind="bar")
    plt.title("Top 10 UFs por Número de Deputados em Órgãos")
    plt.xlabel("UF")
    plt.ylabel("Número de Deputados")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top10_ufs.png"))
    plt.close()

def main():
    df = carregar()
    stats = gerar_tabelas(df)
    gerar_graficos(df, stats)
    print("Análises geradas em:", OUTPUT_DIR)

if __name__ == '__main__':
    main()
