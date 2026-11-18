"""Features do modelo final (etapa 7, passo 2): lags de casos + época do ano.

O notebook de modelos e o dashboard usam esta mesma função, pra as features
serem calculadas exatamente igual no treino e na previsão.
"""

import numpy as np
import pandas as pd

# A ordem importa: o modelo foi treinado com as colunas nesta ordem
FEATURES_MODELO = [
    "casos_lag1",
    "casos_lag2",
    "casos_lag3",
    "casos_lag4",
    "semana_seno",
    "semana_cosseno",
]


def criar_features(dados):
    # Espera a tabela semanal em ordem cronológica e sem semana pulada, com as colunas casos_est e SE
    tabela = dados.copy()

    # Casos das 4 semanas anteriores (lag 1 = semana anterior)
    for k in range(1, 5):
        tabela[f"casos_lag{k}"] = tabela["casos_est"].shift(k)

    # Época do ano como ponto num círculo: a semana 52 fica colada na semana 1
    semana_do_ano = tabela["SE"] % 100
    angulo = 2 * np.pi * semana_do_ano / 52
    tabela["semana_seno"] = np.sin(angulo)
    tabela["semana_cosseno"] = np.cos(angulo)

    return tabela


def semana_epidemiologica(data_inicio):
    # Recebe o domingo que abre a semana e devolve a SE no formato AAAASS (ex.: 202642)
    # A semana pertence ao ano da sua quarta-feira (assim a semana de 29/12/2024 já é a 1 de 2025)
    # Conferido nos dados: bate com a SE do InfoDengue nas 615 semanas, inclusive nos anos com semana 53
    quarta = data_inicio + pd.Timedelta(days=3)
    numero = (quarta.dayofyear - 1) // 7 + 1
    return quarta.year * 100 + numero


def adicionar_proxima_semana(dados):
    # Acrescenta uma linha vazia pra semana seguinte à última da tabela, pra calcular as features dela
    # (os lags dessa linha são os casos das 4 últimas semanas conhecidas)
    ultima_data = dados["data_iniSE"].max()
    proxima_data = ultima_data + pd.Timedelta(days=7)
    proxima = pd.DataFrame({
        "data_iniSE": [proxima_data],
        "SE": [semana_epidemiologica(proxima_data)],
    })
    return pd.concat([dados, proxima], ignore_index=True)
