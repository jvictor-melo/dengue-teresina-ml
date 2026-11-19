"""Dashboard do projeto: previsão semanal de dengue em Teresina.

Rodar a partir da raiz do projeto:
    streamlit run app/app.py
"""

import json
import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# Raiz do projeto = a pasta acima de app/. Assim os caminhos funcionam de onde quer que o app seja aberto
RAIZ = Path(__file__).resolve().parent.parent

# Deixa o Python achar a pasta src/ (mesmo truque do sys.path.append("..") nos notebooks)
sys.path.append(str(RAIZ))
from src.avaliacao import ANOS_TESTE, aplicar_faixa, erros_por_ano
from src.features import FEATURES_MODELO, adicionar_proxima_semana, criar_features

CAMINHO_DADOS = RAIZ / "data" / "processed" / "dengue_clima_semanal.csv"
CAMINHO_MODELO = RAIZ / "models" / "modelo_final.joblib"
CAMINHO_INFO = RAIZ / "models" / "modelo_final.json"
CAMINHO_BACKTEST = RAIZ / "models" / "backtest_modelo_final.csv"
CAMINHO_ABLACAO = RAIZ / "models" / "ablacao.csv"

# Configuração da página: tem que vir antes de qualquer outro comando do Streamlit
st.set_page_config(page_title="Dengue em Teresina", layout="wide")


# O Streamlit roda o script inteiro de novo a cada clique do usuário.
# Os decorators de cache guardam o resultado da primeira vez, pra não reler o arquivo toda hora
# (igual memoização no JS: mesma entrada, devolve o resultado guardado)
@st.cache_data
def carregar_dados():
    dados = pd.read_csv(CAMINHO_DADOS, parse_dates=["data_iniSE"])
    return dados[["data_iniSE", "SE", "casos_est", "semana_aberta"]]


@st.cache_resource
def carregar_modelo():
    modelo = joblib.load(CAMINHO_MODELO)
    with open(CAMINHO_INFO, encoding="utf-8") as arquivo:
        info = json.load(arquivo)
    return modelo, info


@st.cache_data
def carregar_avaliacao():
    # Resultados gerados pelo notebook 06_modelos: o app só lê, não recalcula nenhum modelo
    backtest = pd.read_csv(CAMINHO_BACKTEST, parse_dates=["data_iniSE"])
    ablacao = pd.read_csv(CAMINHO_ABLACAO)
    return backtest, ablacao


dados = carregar_dados()
modelo, info_modelo = carregar_modelo()
backtest, ablacao = carregar_avaliacao()

# --- Previsão da próxima semana ---
# Acrescenta a semana seguinte à última conhecida e calcula as features com a mesma função do treino
com_proxima = criar_features(adicionar_proxima_semana(dados))
linha_proxima = com_proxima.iloc[[-1]]
previsao = modelo.predict(linha_proxima[FEATURES_MODELO])[0]

# Faixa de 80%, com os quantis do erro da janela móvel guardados na ficha do modelo
faixa = info_modelo["faixa_80"]
faixa_baixa, faixa_alta = aplicar_faixa(np.array([previsao]), faixa["quantil_10_log"], faixa["quantil_90_log"])
faixa_baixa = faixa_baixa[0]
faixa_alta = faixa_alta[0]

ultima_semana = dados["data_iniSE"].max()
proxima_semana = linha_proxima["data_iniSE"].iloc[0]
casos_ultima_semana = dados["casos_est"].iloc[-1]

# Ano típico: a mediana de casos de cada semana do ano, só nas semanas fechadas (igual na EDA)
fechadas = dados[~dados["semana_aberta"]]
mediana_por_semana = fechadas.groupby(fechadas["SE"] % 100)["casos_est"].median()

st.title("Previsão semanal de dengue em Teresina")
st.caption(f"Dados do InfoDengue e do ERA5 até a semana de {ultima_semana:%d/%m/%Y}.")

aba_previsao, aba_avaliacao = st.tabs(["Previsão", "Como o modelo foi avaliado"])

with aba_previsao:
    coluna_previsao, coluna_faixa = st.columns(2)

    # delta_color="inverse": subir casos aparece em vermelho, cair aparece em verde
    coluna_previsao.metric(
        f"Previsão para a semana de {proxima_semana:%d/%m/%Y}",
        f"{previsao:.0f} casos",
        delta=f"{previsao - casos_ultima_semana:+.0f} em relação à semana anterior",
        delta_color="inverse",
    )
    coluna_faixa.metric("Faixa provável (80%)", f"{faixa_baixa:.0f} a {faixa_alta:.0f} casos")

    st.caption(
        f"A faixa vem dos erros do modelo nas semanas de teste de 2019 a 2026: o número real ficou dentro dela "
        f"em {faixa['cobertura_janela_movel'] * 100:.0f}% das semanas. Nos anos fora do comum (como 2021 e o surto "
        f"de 2022) ela acertou menos."
    )

    st.warning(
        "As semanas mais recentes ainda estão sendo notificadas e os números delas costumam subir nas próximas "
        "atualizações. Como a previsão usa essas semanas, ela tende a sair um pouco abaixo do que vai acontecer."
    )

    # Gráfico: últimas 12 semanas, a previsão no fim e o ano típico ao fundo
    # 12 e não mais: depois de um pico grande, o eixo ia até centenas de casos e a previsão sumia no canto de baixo
    recentes = dados.tail(12)
    recentes_fechadas = recentes[~recentes["semana_aberta"]]
    recentes_abertas = recentes[recentes["semana_aberta"]]

    # A linha tracejada começa na última semana fechada, pra as duas linhas se encostarem
    if len(recentes_fechadas) > 0:
        recentes_abertas = pd.concat([recentes_fechadas.tail(1), recentes_abertas])

    datas_tipico = pd.concat([recentes["data_iniSE"], linha_proxima["data_iniSE"]])
    semanas_tipico = pd.concat([recentes["SE"], linha_proxima["SE"]]) % 100
    valores_tipico = semanas_tipico.map(mediana_por_semana)

    fig, eixo = plt.subplots(figsize=(11, 4))
    eixo.plot(datas_tipico, valores_tipico, color="gray", linestyle=":", label="ano típico (mediana 2015–2026)")
    # Com 20 semanas abertas, as 12 últimas costumam ser todas abertas: aí não tem linha cheia pra desenhar
    if len(recentes_fechadas) > 0:
        eixo.plot(recentes_fechadas["data_iniSE"], recentes_fechadas["casos_est"], color="black", marker="o", markersize=3, label="casos (fechados)")
    eixo.plot(recentes_abertas["data_iniSE"], recentes_abertas["casos_est"], color="black", linestyle="--", marker="o", markersize=3, label="casos (ainda mudam)")

    # errorbar desenha o ponto da previsão com a faixa (a distância até a ponta de baixo e até a de cima)
    eixo.errorbar(
        [proxima_semana], [previsao],
        yerr=[[previsao - faixa_baixa], [faixa_alta - previsao]],
        color="red", marker="o", capsize=6, label="previsão e faixa de 80%",
    )

    eixo.set_ylabel("casos estimados por semana")
    eixo.legend(loc="upper right")
    st.pyplot(fig)

with aba_avaliacao:
    st.markdown(
        "Pra cada ano de 2019 a 2026, o modelo foi treinado só com os anos anteriores e testado naquele ano "
        "(janela móvel). A comparação é com o **baseline**: prever que a semana que vem vai ter os mesmos casos "
        "desta. Só entram semanas que já fecharam."
    )

    # Erro por ano e total, com a mesma função usada no notebook
    erros_modelo = erros_por_ano(backtest, "previsao_modelo")
    erros_baseline = erros_por_ano(backtest, "previsao_baseline")
    total_modelo = erros_modelo[erros_modelo["ano"] == "total"].iloc[0]
    total_baseline = erros_baseline[erros_baseline["ano"] == "total"].iloc[0]

    # Resumo: delta negativo = o modelo errou menos que o baseline (por isso "inverse": negativo fica verde)
    coluna_mae, coluna_rmse, coluna_semanas = st.columns(3)
    coluna_mae.metric(
        "Erro médio (MAE)",
        f"{total_modelo['MAE']:.1f} casos/semana",
        delta=f"{total_modelo['MAE'] - total_baseline['MAE']:.1f} vs baseline ({total_baseline['MAE']:.1f})",
        delta_color="inverse",
    )
    coluna_rmse.metric(
        "RMSE (pesa mais os erros grandes)",
        f"{total_modelo['RMSE']:.1f}",
        delta=f"{total_modelo['RMSE'] - total_baseline['RMSE']:.1f} vs baseline ({total_baseline['RMSE']:.1f})",
        delta_color="inverse",
    )
    coluna_semanas.metric("Semanas testadas", len(backtest))

    # Previsto x real num ano escolhido (selectbox = um <select>)
    st.subheader("Previsto x real")
    ano_escolhido = st.selectbox("Ano de teste", ANOS_TESTE, index=ANOS_TESTE.index(2025))
    do_ano = backtest[backtest["ano"] == ano_escolhido]

    fig, eixo = plt.subplots(figsize=(11, 4))
    eixo.plot(do_ano["data_iniSE"], do_ano["casos_est"], color="black", label="real")
    eixo.plot(do_ano["data_iniSE"], do_ano["previsao_modelo"], color="red", label="modelo")
    eixo.plot(do_ano["data_iniSE"], do_ano["previsao_baseline"], color="gray", linestyle="--", label="baseline (semana anterior)")
    eixo.set_ylabel("casos estimados por semana")
    eixo.legend(loc="upper right")
    st.pyplot(fig)

    # Erro ano a ano, modelo x baseline
    st.subheader("Erro médio por ano (MAE)")
    # A diferença é calculada com os valores cheios e só depois arredondada (senão 2,04 - 0,05 viraria 1,9)
    por_ano = pd.DataFrame({
        "ano": erros_modelo["ano"].astype(str),
        "modelo": erros_modelo["MAE"].round(1),
        "baseline": erros_baseline["MAE"].round(1),
        "diferença": (erros_modelo["MAE"] - erros_baseline["MAE"]).round(1),
    })
    st.dataframe(por_ano, hide_index=True)
    st.caption("Diferença negativa: o modelo errou menos que o baseline naquele ano.")

    # Os modelos testados antes de escolher o final
    st.subheader("O que foi testado")
    st.dataframe(ablacao, hide_index=True)
    st.caption(
        "Cada passo acrescenta uma coisa por vez, avaliado nas mesmas semanas. O clima (chuva e umidade do ERA5) "
        "não melhorou a previsão de 1 semana à frente, o log ajudou só nos anos calmos e o Gradient Boosting foi "
        "instável entre os anos."
    )

    st.subheader("Limitações")
    st.markdown(
        "- As semanas mais recentes ainda são provisórias: a previsão da próxima semana usa números que vão mudar.\n"
        "- No teste, as semanas anteriores aparecem com o número já revisado, que não existia na hora. Como as "
        "semanas recentes chegam a subir até 87% nas atualizações seguintes, o erro no uso real deve ser maior que "
        "o mostrado aqui, pro modelo e pro baseline.\n"
        "- O ganho sobre o baseline é pequeno e não acontece em todos os anos.\n"
        "- O clima vem do ERA5 (grade de ~25 km), que suaviza a chuva localizada.\n"
        "- O painel usa uma cópia fixa dos dados, não a API ao vivo."
    )
