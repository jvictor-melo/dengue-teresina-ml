"""Previsão da próxima semana, usada pelo dashboard (app/app.py) e pelo script do site.

Fica num lugar só pra os dois mostrarem sempre o mesmo número.
"""

import numpy as np
import pandas as pd

from src.avaliacao import aplicar_faixa
from src.features import FEATURES_MODELO, adicionar_proxima_semana, criar_features


def mediana_por_semana(dados):
    # Ano típico: a mediana de casos de cada semana do ano, só nas semanas fechadas (igual na EDA)
    # SQL: SELECT SE % 100, MEDIAN(casos_est) FROM dados WHERE NOT semana_aberta GROUP BY SE % 100
    fechadas = dados[~dados["semana_aberta"]]
    return fechadas.groupby(fechadas["SE"] % 100)["casos_est"].median()


def status_da_epoca(faixa_min, faixa_max, mediana):
    # Compara a faixa da previsão com o normal daquela semana do ano
    # A régua é a própria faixa de 80% do modelo: só sai do "normal" se a faixa inteira ficar de um lado
    if faixa_max < mediana:
        return "abaixo"
    if faixa_min > mediana:
        return "acima"
    return "normal"


def prever_proxima_semana(dados, modelo, info):
    # Acrescenta a semana seguinte à última conhecida e calcula as features com a mesma função do treino
    com_proxima = criar_features(adicionar_proxima_semana(dados))
    linha_proxima = com_proxima.iloc[[-1]]
    previsto = modelo.predict(linha_proxima[FEATURES_MODELO])[0]

    # Casos negativos não existem: se a conta der abaixo de zero, a previsão vira zero
    casos = max(0.0, float(previsto))

    # Faixa de 80%, com os quantis do erro da janela móvel guardados na ficha do modelo
    faixa = info["faixa_80"]
    faixa_min, faixa_max = aplicar_faixa(np.array([previsto]), faixa["quantil_10_log"], faixa["quantil_90_log"])
    # Com previsão 0, expm1(0 - 0,62) dá -0,46: o piso da faixa também não pode ser negativo
    faixa_min = np.clip(faixa_min, 0, None)

    semana = linha_proxima["data_iniSE"].iloc[0]
    se = int(linha_proxima["SE"].iloc[0])
    # A semana 53 só existe em alguns anos e pode não ter mediana: nesse caso usa a da semana 52
    medianas = mediana_por_semana(dados)
    semana_do_ano = se % 100
    if semana_do_ano == 53 and 53 not in medianas.index:
        semana_do_ano = 52
    mediana = float(medianas[semana_do_ano])

    return {
        "semana": semana,
        # A semana vai de domingo a sábado: o sábado é o domingo + 6 dias
        "semana_fim": semana + pd.Timedelta(days=6),
        "SE": se,
        "casos": casos,
        "faixa_min": float(faixa_min[0]),
        "faixa_max": float(faixa_max[0]),
        "mediana_epoca": mediana,
        "status": status_da_epoca(float(faixa_min[0]), float(faixa_max[0]), mediana),
    }


def semanas_recentes(dados, n=12):
    # As últimas n semanas, pro gráfico (12 e não mais: depois de um pico grande, a previsão sumia no canto do eixo)
    # SE junto: o dashboard usa pra desenhar a linha do ano típico embaixo
    return dados[["data_iniSE", "SE", "casos_est", "semana_aberta"]].tail(n)
