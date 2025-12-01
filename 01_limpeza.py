#!/usr/bin/env python3
# 01_limpeza.py
# Script responsável pela limpeza e unificação das bases orgaosDeputados-L*.csv
# Saída: /mnt/data/orgaos_analysis_outputs/orgaos_deputados_limpo.csv

import os, glob, pandas as pd

INPUT_GLOB = "/mnt/data/orgaosDeputados-L*.csv"
DEPUTADOS_GLOB = "/mnt/data/deputados*.csv"
OUTPUT_DIR = "/mnt/data/orgaos_analysis_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def carregar_orgaos(pattern=INPUT_GLOB):
    arquivos = sorted(glob.glob(pattern))
    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo orgaosDeputados encontrado em " + pattern)
    dfs = []
    for path in arquivos:
        nome = os.path.basename(path)
        try:
            df = pd.read_csv(path, sep=";", encoding="utf-8", low_memory=False)
        except Exception:
            df = pd.read_csv(path, sep=";", encoding="latin-1", low_memory=False)
        df.columns = [c.strip() for c in df.columns]
        # Extrair legislatura do nome do arquivo (ex: orgaosDeputados-L51.csv)
        try:
            leg = "L" + nome.split("-L")[1].split(".")[0].strip().split()[0]
        except Exception:
            leg = None
        df["legislatura"] = leg
        dfs.append(df)
    all_df = pd.concat(dfs, ignore_index=True, sort=False)
    return all_df

def carregar_deputados(pattern=DEPUTADOS_GLOB):
    arquivos = sorted(glob.glob(pattern))
    if not arquivos:
        return pd.DataFrame()
    path = arquivos[0]
    try:
        df = pd.read_csv(path, sep=";", encoding="utf-8", low_memory=False)
    except Exception:
        df = pd.read_csv(path, sep=";", encoding="latin-1", low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    if "uri" in df.columns and "uriDeputado" not in df.columns:
        df = df.rename(columns={"uri": "uriDeputado"})
    return df

def tratar(df_orgs, df_deputados):
    df = df_orgs.copy()
    expected = ["uriOrgao","siglaOrgao","nomeOrgao","nomePublicacaoOrgao",
                "uriDeputado","nomeDeputado","siglaPartido","siglaUF","cargo",
                "dataInicio","dataFim","legislatura"]
    for col in expected:
        if col not in df.columns:
            df[col] = pd.NA

    # preencher siglaUF com ufNascimento se disponível
    if "ufNascimento" in df_deputados.columns:
        complemento = df_deputados[["uriDeputado","ufNascimento","siglaSexo"]].drop_duplicates(subset=["uriDeputado"])
        df = df.merge(complemento, on="uriDeputado", how="left")
        df["siglaUF"] = df["siglaUF"].fillna(df.get("ufNascimento"))
        if "siglaSexo" in df.columns:
            df = df.rename(columns={"siglaSexo":"sexoDeputado"})
        if "ufNascimento" in df.columns:
            df = df.drop(columns=["ufNascimento"], errors="ignore")
    else:
        df["sexoDeputado"] = pd.NA

    df["siglaPartido"] = df["siglaPartido"].fillna("Desconhecido")
    df["siglaUF"] = df["siglaUF"].fillna("Desconhecido")

    df["dataInicio"] = pd.to_datetime(df["dataInicio"], errors="coerce")
    df["dataFim"] = pd.to_datetime(df["dataFim"], errors="coerce")

    # remover duplicatas exatas
    df = df.drop_duplicates()

    # remover registros com dataInicio > dataFim
    cond = df["dataFim"].notna() & (df["dataInicio"] > df["dataFim"])
    if cond.sum() > 0:
        df = df[~cond]

    # reordenar colunas
    cols_order = ["legislatura","uriOrgao","siglaOrgao","nomeOrgao","nomePublicacaoOrgao",
                  "uriDeputado","nomeDeputado","sexoDeputado","siglaPartido","siglaUF",
                  "cargo","dataInicio","dataFim"]
    existing = [c for c in cols_order if c in df.columns]
    other = [c for c in df.columns if c not in existing]
    df = df[existing + other]
    return df

def main():
    print("Carregando arquivos de órgãos...")
    df_orgs = carregar_orgaos()
    print(f"Registros carregados (orgaos): {len(df_orgs)}")
    df_deputados = carregar_deputados()
    print(f"Registros carregados (deputados): {len(df_deputados)}")
    df_limpo = tratar(df_orgs, df_deputados)
    caminho = os.path.join(OUTPUT_DIR, "orgaos_deputados_limpo.csv")
    df_limpo.to_csv(caminho, index=False, sep=";")
    print("Arquivo limpo salvo em:", caminho)
    print("Finalizado. Linhas finais:", len(df_limpo))

if __name__ == '__main__':
    main()
