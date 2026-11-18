"""Features do modelo final (etapa 7, passo 2): lags de casos + época do ano.

O notebook de modelos e o dashboard usam esta mesma função, pra as features
serem calculadas exatamente igual no treino e na previsão.
"""

import numpy as np

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
