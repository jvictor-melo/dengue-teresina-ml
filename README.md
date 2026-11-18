# Previsão de dengue em Teresina

Modelo para prever os casos semanais de dengue em Teresina (PI), usando dados públicos do InfoDengue, do INMET e do ERA5. Feito em Python, com pandas e Jupyter.

**Projeto em andamento.** A coleta e a limpeza dos casos estão prontas; agora estou juntando os dados de clima.

## Motivação

Entre 2015 e 2026, o pior momento da dengue em Teresina foi em abril de 2022, com 1.581 casos numa única semana. A ideia é prever essa subida com algumas semanas de antecedência e, no fim, publicar um dashboard com o histórico e a previsão.

## Dados

- **[InfoDengue](https://info.dengue.mat.br/services/api)**: casos semanais de Teresina, de janeiro de 2015 a outubro de 2026, pela API pública.
- **[ERA5 via Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api)**: chuva, temperatura e umidade de hora em hora, de 2015 a outubro de 2026. É o clima usado no modelo.
- **[INMET](https://portal.inmet.gov.br/dadoshistoricos)**: as mesmas três variáveis, medidas pela estação automática de Teresina (A312), de 2015 a setembro de 2026. Usada para conferir o ERA5.

O InfoDengue também tem dados de clima, mas só a partir de junho de 2023 e sem chuva.

## Decisões até aqui

- **Horizonte:** uma semana à frente no começo; depois, até quatro.
- **Alvo:** `casos_est`, a estimativa do InfoDengue que corrige o atraso das notificações.
- **Semanas em aberto:** as 20 mais recentes ficam fora do treino e da avaliação, porque os números delas ainda mudam.
- **Sem indicadores do InfoDengue:** `Rt` e nível de alerta são calculados a partir dos próprios casos e dariam ao modelo uma dica da resposta.
- **Clima do ERA5 no período todo:** a ideia inicial era usar a estação A312 e completar os buracos com o ERA5. Comparando as duas, a chuva mudava de relação ano a ano (em 2015 o ERA5 marcou 85% a mais que a estação; em 2022, 32% a menos), e emendar criaria degraus falsos no clima. A A312 ficou como referência para conferir o ERA5.
- **Dado bruto congelado:** cópia fixa em `data/raw/`, para os resultados serem reproduzíveis.

O porquê de cada uma, e o que eu conferi nos dados antes de decidir, está em [docs/decisoes.md](docs/decisoes.md).

## Estrutura

```
data/raw/          dados brutos, sem alteração
data/processed/    dados tratados pelos notebooks
docs/              decisões e conferências
notebooks/         01_coleta, 02_limpeza, 03_clima
src/               funções reaproveitáveis
models/            modelos treinados
```

## Como rodar

```bash
git clone https://github.com/jvictor-melo/dengue-teresina-ml.git
cd dengue-teresina-ml

python -m venv .venv
.venv\Scripts\Activate.ps1        # no Linux/macOS: source .venv/bin/activate

pip install -r requirements.txt
jupyter notebook
```

Os notebooks rodam em ordem. Os dados já estão no repositório; os ZIPs completos do INMET (cerca de 100 MB por ano) ficam de fora, só o CSV da estação de Teresina é versionado.

## Próximos passos

- Juntar o clima semanal com os casos
- Análise exploratória: sazonalidade e quanto tempo a chuva leva para aparecer nos casos
- Baseline ("a semana que vem é igual a esta") e primeiros modelos, avaliados no tempo
- Dashboard em Streamlit

## Sobre o uso de IA

O planejamento é meu: defini o problema, o horizonte, o alvo, a regra das semanas em aberto e o roteiro das etapas. Usei o Claude Code como copiloto dentro desse plano. Ele escreveu boa parte do código e, em cada passo, levantava os riscos e as alternativas de implementação; eu escolhia o caminho, rodava e conferia os números antes de seguir. As decisões, os textos dos notebooks e deste README e os commits são meus.

Na prática, foi conferindo o dado que algumas decisões mudaram: as semanas em aberto passaram de 10 para 20 depois de comparar dois downloads da API, o ERA5 entrou no projeto depois de medir, ano a ano, que a estação do INMET tinha ficado parada por um ano e meio, e virou a fonte principal do clima depois de comparar as duas fontes semana a semana.

## Créditos dos dados

Casos: [InfoDengue](https://info.dengue.mat.br/). Clima: [INMET](https://portal.inmet.gov.br/) e ERA5 via [Open-Meteo](https://open-meteo.com/) (Zippenfenig, 2023), gerado com informações do Copernicus Climate Change Service.

---

João Victor Macêdo de Melo · [LinkedIn](https://www.linkedin.com/in/jvictor-melo) · [GitHub](https://github.com/jvictor-melo)
