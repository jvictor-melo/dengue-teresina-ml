# Previsão de dengue em Teresina

Modelo para prever os casos semanais de dengue em Teresina (PI), usando dados públicos do InfoDengue e do INMET. Feito em Python, com pandas e Jupyter.

**Projeto em andamento.** A coleta e a limpeza dos casos estão prontas; agora estou juntando os dados de clima.

## Motivação

Entre 2015 e 2026, o pior momento da dengue em Teresina foi em abril de 2022, com 1.581 casos numa única semana. A ideia é prever essa subida com algumas semanas de antecedência e, no fim, publicar um dashboard com o histórico e a previsão.

## Dados

- **[InfoDengue](https://info.dengue.mat.br/services/api)**: casos semanais de Teresina, de janeiro de 2015 a outubro de 2026, pela API pública.
- **[INMET](https://portal.inmet.gov.br/dadoshistoricos)**: chuva, temperatura e umidade da estação automática de Teresina (A312), de 2015 a setembro de 2026.

O InfoDengue também tem dados de clima, mas só a partir de junho de 2023 e sem chuva. Por isso o clima vem do INMET.

## Decisões até aqui

**Horizonte.** Começo prevendo uma semana à frente, que é mais simples e me deixa validar o pipeline de ponta a ponta. Depois a ideia é chegar a quatro semanas, com um modelo para cada horizonte.

**Alvo.** As notificações de dengue chegam atrasadas, então as semanas mais recentes aparecem com menos casos do que realmente tiveram. Por isso o alvo é o `casos_est`, a estimativa do InfoDengue que corrige esse atraso. Nas semanas antigas, ele é igual ao número notificado.

**Semanas em aberto.** O InfoDengue só corrige as 10 semanas mais recentes. Mas baixei os dados duas vezes, com uma semana de intervalo, e os números mudaram até 20 semanas para trás. Essas 20 semanas ficam fora do treino e da avaliação.

**Colunas que ficaram de fora.** Indicadores como o `Rt` e o nível de alerta são calculados pelo InfoDengue a partir dos próprios casos. Usar isso como entrada seria dar ao modelo uma dica da resposta.

**Dado bruto congelado.** A API revisa os números com o tempo, então guardo uma cópia em `data/raw/` e não mexo mais nela. Assim os resultados podem ser reproduzidos.

## Estrutura

```
data/raw/          dados brutos, sem alteração
data/processed/    dados tratados pelos notebooks
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

Usei o Claude Code para escrever boa parte do código. As decisões acima, a conferência dos números em cada etapa e os textos dos notebooks são meus.

---

João Victor Macêdo de Melo · [LinkedIn](https://www.linkedin.com/in/joaovictormmelo) · [GitHub](https://github.com/jvictor-melo)
