"""Regras de avaliação do projeto (etapa 6), usadas por todos os modelos.

Janela móvel anual: cada ano de 2019 a 2026 é um teste, e o treino é tudo o que veio antes.
Só semanas fechadas entram (as abertas ainda vão mudar). Erro em MAE e RMSE, na escala real de casos.
"""

import numpy as np
import pandas as pd

ANOS_TESTE = list(range(2019, 2027))


def calcular_erros(real, previsto):
    erro = real - previsto
    # MAE: média do tamanho do erro, em casos por semana
    mae = erro.abs().mean()
    # RMSE: eleva o erro ao quadrado antes da média, então erro grande pesa muito mais
    rmse = np.sqrt((erro ** 2).mean())
    return {"MAE": mae, "RMSE": rmse}


def separar_treino_teste(dados, ano_teste):
    # Só semanas fechadas; o treino é tudo antes do ano de teste
    fechadas = dados[~dados["semana_aberta"]]
    treino = fechadas[fechadas["ano"] < ano_teste]
    teste = fechadas[fechadas["ano"] == ano_teste]
    return treino, teste


def erros_por_ano(semanas_avaliadas, coluna_previsao):
    # Recebe as semanas de teste de todos os anos (com a coluna de previsão) e devolve o erro por ano e o total
    linhas = []
    for ano in ANOS_TESTE:
        do_ano = semanas_avaliadas[semanas_avaliadas["ano"] == ano]
        erros = calcular_erros(do_ano["casos_est"], do_ano[coluna_previsao])
        linhas.append({"ano": ano, "MAE": erros["MAE"], "RMSE": erros["RMSE"]})

    total = calcular_erros(semanas_avaliadas["casos_est"], semanas_avaliadas[coluna_previsao])
    linhas.append({"ano": "total", "MAE": total["MAE"], "RMSE": total["RMSE"]})

    return pd.DataFrame(linhas)
