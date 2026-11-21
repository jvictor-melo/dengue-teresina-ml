"""Testes da previsão da próxima semana (src/previsao.py).

Rodar da raiz do projeto:
    python -m pytest tests -v
"""

import json
import sys
from pathlib import Path

import joblib
import pandas as pd

# Mesmo truque do app: deixa o Python achar a pasta src/
RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))
from src.previsao import (
    mediana_por_semana,
    prever_proxima_semana,
    semanas_recentes,
    status_da_epoca,
)


def carregar_tudo():
    # Os mesmos arquivos que o dashboard lê
    dados = pd.read_csv(RAIZ / "data" / "processed" / "dengue_clima_semanal.csv", parse_dates=["data_iniSE"])
    dados = dados[["data_iniSE", "SE", "casos_est", "semana_aberta"]]
    modelo = joblib.load(RAIZ / "models" / "modelo_final.joblib")
    with open(RAIZ / "models" / "modelo_final.json", encoding="utf-8") as arquivo:
        info = json.load(arquivo)
    return dados, modelo, info


def tabela_sintetica(ultima_data, casos):
    # Uma tabela de mentirinha com as semanas que terminam em ultima_data, todas fechadas
    datas = pd.date_range(end=ultima_data, periods=len(casos), freq="7D")
    from src.features import semana_epidemiologica
    return pd.DataFrame({
        "data_iniSE": datas,
        "SE": [semana_epidemiologica(d) for d in datas],
        "casos_est": casos,
        "semana_aberta": False,
    })


def test_status_da_epoca():
    # A mediana dentro da faixa = normal; a faixa toda abaixo ou toda acima = abaixo/acima
    assert status_da_epoca(10, 29, 14) == "normal"
    assert status_da_epoca(5, 12, 14) == "abaixo"
    assert status_da_epoca(432, 1248, 275) == "acima"


def test_previsao_atual():
    # Os números que o dashboard mostra hoje (gabarito anotado antes da mudança)
    dados, modelo, info = carregar_tudo()
    resultado = prever_proxima_semana(dados, modelo, info)
    assert resultado["semana"] == pd.Timestamp("2026-11-15")
    assert round(resultado["casos"]) == 19
    assert round(resultado["faixa_min"]) == 10
    assert round(resultado["faixa_max"]) == 29
    assert resultado["mediana_epoca"] == 14
    assert resultado["status"] == "normal"


def test_previsao_nunca_negativa():
    # Um ano inteiro com zero caso até setembro: a época puxa a previsão pra baixo de zero
    # (60 semanas, pra toda semana do ano ter uma mediana)
    dados = tabela_sintetica("2026-09-13", [0] * 60)
    _, modelo, info = carregar_tudo()
    resultado = prever_proxima_semana(dados, modelo, info)
    assert resultado["casos"] >= 0
    assert resultado["faixa_min"] >= 0


def test_virada_de_ano():
    # A última semana conhecida é a de 28/12/2025, então a próxima é a semana 1 de 2026
    # (60 semanas, pra tabela ter uma semana 1 no passado: a de 2025)
    dados = tabela_sintetica("2025-12-28", list(range(60)))
    _, modelo, info = carregar_tudo()
    resultado = prever_proxima_semana(dados, modelo, info)
    assert resultado["semana"] == pd.Timestamp("2026-01-04")
    assert resultado["SE"] == 202601
    # A mediana tem que vir da semana 1 (e não da 53 ou da 52)
    assert resultado["mediana_epoca"] == mediana_por_semana(dados)[1]


def test_semanas_recentes():
    dados, _, _ = carregar_tudo()
    recentes = semanas_recentes(dados)
    assert len(recentes) == 12
    assert recentes["data_iniSE"].iloc[-1] == pd.Timestamp("2026-11-08")
    assert list(recentes.columns) == ["data_iniSE", "SE", "casos_est", "semana_aberta"]
