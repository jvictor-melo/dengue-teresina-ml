"""Testes do script que gera o previsao.json do site (scripts/gerar_previsao.py)."""

import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))
from scripts.gerar_previsao import carregar_dados_e_modelo, montar_contexto, montar_json


def test_contexto():
    # Números da tela 1, conferidos com a EDA (dados de 18/11/2026)
    dados, _, _ = carregar_dados_e_modelo()
    contexto = montar_contexto(dados)
    # 62,5 com uma casa (a EDA mostra 62,4 porque soma os 3 meses já arredondados)
    assert contexto["pct_mar_mai"] == 62.5
    assert contexto["casos_2022"] == 16170
    assert contexto["ano_atual"] == 2026
    assert contexto["casos_ano_atual_fechados"] == 9263
    assert contexto["ultima_semana_fechada"] == "2026-06-21"
    assert contexto["semana_pico_tipico"] == 15


def test_json_formato():
    dados, modelo, info = carregar_dados_e_modelo()
    saida = montar_json(dados, modelo, info, hoje=date(2026, 11, 20))

    assert set(saida.keys()) == {"atualizado_em", "dados_ate", "dados_ate_fim", "previsao", "recentes", "contexto"}
    assert saida["atualizado_em"] == "2026-11-20"
    assert saida["dados_ate"] == "2026-11-08"
    assert saida["dados_ate_fim"] == "2026-11-14"

    previsao = saida["previsao"]
    assert previsao["semana"] == "2026-11-15"
    assert previsao["semana_fim"] == "2026-11-21"
    assert previsao["casos"] == 19
    assert previsao["faixa_min"] == 10
    assert previsao["faixa_max"] == 29
    assert previsao["mediana_epoca"] == 14
    assert previsao["status"] in {"abaixo", "normal", "acima"}
    assert 0.79 < previsao["cobertura"] < 0.81

    assert len(saida["recentes"]) == 12
    assert saida["recentes"][-1] == {"semana": "2026-11-08", "casos": 20, "aberta": True}

    # allow_nan=False: se tiver NaN em algum lugar, dá erro (NaN não é JSON válido e quebraria o site)
    json.dumps(saida, allow_nan=False)
