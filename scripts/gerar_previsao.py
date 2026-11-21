"""Gera o web/public/previsao.json, que é tudo o que o site lê.

Rodar da raiz do projeto, depois de atualizar os dados (notebooks 01 a 03):
    python scripts/gerar_previsao.py

Só lê data/processed/ e models/. Não baixa nada e não mexe em data/raw/.
"""

import json
import sys
from datetime import date
from pathlib import Path

import joblib
import pandas as pd

# Raiz do projeto = a pasta acima de scripts/ (mesmo truque do app)
RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))
from src.previsao import mediana_por_semana, prever_proxima_semana, semanas_recentes

CAMINHO_DADOS = RAIZ / "data" / "processed" / "dengue_clima_semanal.csv"
CAMINHO_MODELO = RAIZ / "models" / "modelo_final.joblib"
CAMINHO_INFO = RAIZ / "models" / "modelo_final.json"
CAMINHO_SAIDA = RAIZ / "web" / "public" / "previsao.json"


def carregar_dados_e_modelo():
    # Os mesmos arquivos e as mesmas colunas que o dashboard usa
    dados = pd.read_csv(CAMINHO_DADOS, parse_dates=["data_iniSE"])
    dados = dados[["data_iniSE", "SE", "casos_est", "semana_aberta"]]
    modelo = joblib.load(CAMINHO_MODELO)
    with open(CAMINHO_INFO, encoding="utf-8") as arquivo:
        info = json.load(arquivo)
    return dados, modelo, info


def montar_contexto(dados):
    # Números da tela 1. Só semanas fechadas, como na EDA (as abertas ainda vão mudar)
    fechadas = dados[~dados["semana_aberta"]]
    ano = fechadas["SE"] // 100
    mes = fechadas["data_iniSE"].dt.month

    total = fechadas["casos_est"].sum()
    mar_mai = fechadas[mes.isin([3, 4, 5])]["casos_est"].sum()
    ano_atual = int(ano.max())

    return {
        "pct_mar_mai": round(float(mar_mai / total * 100), 1),
        "casos_2022": int(fechadas[ano == 2022]["casos_est"].sum()),
        "ano_atual": ano_atual,
        "casos_ano_atual_fechados": int(fechadas[ano == ano_atual]["casos_est"].sum()),
        "ultima_semana_fechada": fechadas["data_iniSE"].max().strftime("%Y-%m-%d"),
        # Semana do ano com a maior mediana de casos (o pico do "ano típico")
        "semana_pico_tipico": int(mediana_por_semana(dados).idxmax()),
    }


def montar_json(dados, modelo, info, hoje):
    resultado = prever_proxima_semana(dados, modelo, info)

    # Lista de dicionários pro gráfico: no JSON vira um array de objetos, como no JS
    recentes = []
    for _, linha in semanas_recentes(dados).iterrows():
        recentes.append({
            "semana": linha["data_iniSE"].strftime("%Y-%m-%d"),
            "casos": int(round(linha["casos_est"])),
            "aberta": bool(linha["semana_aberta"]),
        })

    return {
        "atualizado_em": hoje.isoformat(),
        "dados_ate": dados["data_iniSE"].max().strftime("%Y-%m-%d"),
        # Sábado da última semana de dados: o site mostra a semana inteira ("8 a 14 de novembro")
        "dados_ate_fim": (dados["data_iniSE"].max() + pd.Timedelta(days=6)).strftime("%Y-%m-%d"),
        "previsao": {
            "semana": resultado["semana"].strftime("%Y-%m-%d"),
            "semana_fim": resultado["semana_fim"].strftime("%Y-%m-%d"),
            # O site mostra inteiros: arredonda aqui, uma vez só
            "casos": int(round(resultado["casos"])),
            "faixa_min": int(round(resultado["faixa_min"])),
            "faixa_max": int(round(resultado["faixa_max"])),
            "mediana_epoca": int(round(resultado["mediana_epoca"])),
            "status": resultado["status"],
            "cobertura": round(info["faixa_80"]["cobertura_janela_movel"], 3),
        },
        "recentes": recentes,
        "contexto": montar_contexto(dados),
    }


def main():
    dados, modelo, info = carregar_dados_e_modelo()
    saida = montar_json(dados, modelo, info, hoje=date.today())

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(CAMINHO_SAIDA, "w", encoding="utf-8") as arquivo:
        # ensure_ascii=False mantém os acentos legíveis; allow_nan=False garante JSON válido
        json.dump(saida, arquivo, ensure_ascii=False, indent=2, allow_nan=False)

    previsao = saida["previsao"]
    print(f"Salvo em {CAMINHO_SAIDA}")
    print(f"Semana de {previsao['semana']}: {previsao['casos']} casos "
          f"(faixa {previsao['faixa_min']} a {previsao['faixa_max']}), status {previsao['status']}")


if __name__ == "__main__":
    main()
