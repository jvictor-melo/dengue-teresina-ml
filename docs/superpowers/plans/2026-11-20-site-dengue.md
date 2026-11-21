# Site "Dengue em Teresina": plano de implementação

> **Para quem executa:** modo COPILOTO (ver `CLAUDE.md`). **Uma tarefa por vez.** Antes de cada uma: explicar o objetivo e esperar o ok do João. No fim de cada uma: explicar bloco por bloco, mostrar como conferir e **sugerir** a mensagem de commit. Quem commita é o João, nunca o executor. Nenhum pacote é instalado sem explicar o que é e pedir o ok. Passos com checkbox (`- [ ]`).

**Objetivo:** site estático de uma página que mostra o contexto da dengue em Teresina e a previsão da próxima semana, lendo um `previsao.json` gerado pelo modelo do projeto.

**Arquitetura:** a lógica de previsão sai do `app/app.py` e vira `src/previsao.py`, que o Streamlit e um script novo passam a usar. O script escreve `web/public/previsao.json`. O site (Vite + React, em `web/`) só lê esse JSON. Deploy na Vercel com a pasta raiz `web/`.

**Stack:** Python 3.14 (pandas, scikit-learn, joblib, já na `.venv`) · Vite + React · SVG feito à mão · Google Fonts (Instrument Serif + Manrope) · Vercel.

**Spec:** `docs/superpowers/specs/2026-11-20-site-dengue-design.md` (as seções 5 e 8 valem; quando houver conflito, a 8 ganha). Mockups em `docs/superpowers/specs/mockups/`.

## Restrições globais
- `data/raw/` é intocável. O script só lê `data/processed/` e `models/`.
- **O Streamlit tem que mostrar exatamente os mesmos números** antes e depois da refatoração.
- Nenhum número digitado à mão no site: tudo sai do JSON.
- Paleta: fundo ~`#0b0b0b`, cartão `#141414`, texto creme `#f2efe6`, amarelo `#f5c518`. Sem verde e sem vermelho.
- Selo: `abaixo` → "Abaixo do normal pra época" (contorno creme) · `normal` → "Normal pra época" (contorno amarelo) · `acima` → "Acima do normal pra época" (amarelo cheio, texto preto).
- Texto mínimo de 13px pra aviso e legendas, sem transparência que derrube o contraste.
- Textos fixos (copiar exatamente):
  - "Todo ano, entre março e maio."
  - "A temporada da dengue"
  - "Pra evitar o mosquito: não deixe água parada em vasos, pneus e caixas d'água."
  - "Previsão de um modelo estatístico, não é dado oficial."
  - "semanas ainda sendo atualizadas (os números costumam subir)"
- Números em formato brasileiro (`16.170`, `1.248`).
- `prefers-reduced-motion`: tudo aparece pronto, sem animação.
- Comentários em português. Código simples (o Python do João é básico).

## Foco da revisão
1. **Previsão negativa ou zero** (o passo 2 da ablação já teve mínimo de 0,1): o número e a faixa nunca podem ser negativos. A faixa já usa `clip`, mas o número precisa de `max(0, ...)`. → teste na Tarefa 1.
2. **JSON não carrega** (404, rede): o site mostra "Não foi possível carregar a previsão agora." em vez de tela vazia ou quebrada. → verificação na Tarefa 4.
3. **Previsão velha:** se `atualizado_em` tiver mais de 14 dias, mostrar a data em destaque ("Atualizado há X dias"). → Tarefa 4.
4. **Semanas mistas no gráfico** (algumas fechadas, outras abertas): a linha cheia vira tracejada na primeira aberta, sem buraco no meio. → teste na Tarefa 1 (o campo `aberta` por semana) + verificação na Tarefa 5.
5. **Virada de ano / semana 53:** a próxima semana depois da última de dezembro tem a SE certa e a mediana certa. → teste na Tarefa 1.

---

### Tarefa 1: lógica de previsão compartilhada em `src/previsao.py`

**Arquivos:**
- Criar: `src/previsao.py`
- Criar: `tests/test_previsao.py`
- Modificar: `app/app.py` (o bloco "Previsão da próxima semana", a mediana por semana e as 12 semanas recentes)

**Interfaces (produz):**
- `mediana_por_semana(dados: DataFrame) -> Series`: mediana de `casos_est` por semana do ano (`SE % 100`), só semanas fechadas.
- `status_da_epoca(faixa_min: float, faixa_max: float, mediana: float) -> str`: devolve `"abaixo"` se `faixa_max < mediana`, `"acima"` se `faixa_min > mediana`, senão `"normal"`.
- `prever_proxima_semana(dados, modelo, info) -> dict` com as chaves `semana` (Timestamp), `SE` (int), `casos`, `faixa_min`, `faixa_max`, `mediana_epoca` (floats ≥ 0) e `status` (str).
- `semanas_recentes(dados, n=12) -> DataFrame` com as colunas `data_iniSE`, `casos_est`, `semana_aberta`.

> ⚠️ Antes: o projeto não tem `pytest`. Explicar o que é (o "Jest do Python") e pedir o ok pra `pip install pytest`. Se o João não quiser, os testes viram um script `python tests/test_previsao.py` com `assert`.

- [ ] **Passo 1: rodar o Streamlit atual com `AppTest` e anotar os números** (previsão, faixa, 12 semanas). É o gabarito de "nada mudou". Esperado hoje: previsão 19, faixa 10 a 29.
- [ ] **Passo 2: escrever os testes que falham**
  - `test_status_da_epoca`: `(10, 29, 14) → "normal"`, `(5, 12, 14) → "abaixo"`, `(432, 1248, 275) → "acima"`.
  - `test_previsao_atual`: com os dados e o modelo reais, `round(casos) == 19`, `round(faixa_min) == 10`, `round(faixa_max) == 29`, `mediana_epoca == 14`, `status == "normal"`, `semana == 2026-11-15`.
  - `test_previsao_nunca_negativa`: dados sintéticos com os 4 lags = 0 numa semana de setembro → `casos >= 0` e `faixa_min >= 0`.
  - `test_virada_de_ano`: tabela sintética terminando em 2025-12-28 → `SE == 202601` e `mediana_epoca` lida da semana 1.
  - `test_semanas_recentes`: `len == 12`, a última linha é 2026-11-08, `semana_aberta` preservada.
- [ ] **Passo 3: rodar e ver falhar.** `.venv\Scripts\python -m pytest tests/test_previsao.py -v` → falha com "No module named src.previsao".
- [ ] **Passo 4: implementar as 4 funções em `src/previsao.py`**, reaproveitando `criar_features`, `adicionar_proxima_semana` e `aplicar_faixa`, com `casos = max(0, previsão)`.
- [ ] **Passo 5: rodar e ver passar.**
- [ ] **Passo 6: trocar o `app/app.py`** pra usar as funções (sem mudar textos nem gráficos). Rodar o `AppTest` de novo: os números têm que ser os mesmos do Passo 1.
- [ ] **Passo 7: sugerir o commit:** `refactor: move previsao da semana para src/previsao.py`

### Tarefa 2: script que gera o `previsao.json`

**Arquivos:**
- Criar: `scripts/gerar_previsao.py`
- Criar: `tests/test_gerar_previsao.py`
- Gera: `web/public/previsao.json`

**Interfaces:**
- Usa (Tarefa 1): `prever_proxima_semana`, `semanas_recentes`.
- Produz: `montar_contexto(dados) -> dict` com `pct_mar_mai` (float), `casos_2022` (int), `ano_atual` (int), `casos_ano_atual_fechados` (int), `ultima_semana_fechada` (str ISO) e `semana_pico_tipico` (int, a semana do ano com a maior mediana). Também `montar_json(dados, modelo, info, hoje) -> dict` e `main()`.
- O formato do JSON segue a seção 6.3 da spec, mais:
  - `previsao.mediana_epoca`;
  - `previsao.cobertura` (de `info["faixa_80"]["cobertura_janela_movel"]`);
  - `recentes[].aberta`.
  - Datas em ISO (`"2026-11-15"`). `casos` arredondado pra inteiro no JSON (o site não arredonda).

- [ ] **Passo 1: testes que falham**
  - `test_contexto`: `round(pct_mar_mai) == 62`, `casos_2022 == 16170`, `ano_atual == 2026`, `casos_ano_atual_fechados == 9263`, `ultima_semana_fechada == "2026-06-21"`.
  - `test_json_formato`: chaves de primeiro nível = `{"atualizado_em", "dados_ate", "previsao", "recentes", "contexto"}`, `len(recentes) == 12`, `previsao["status"] in {"abaixo", "normal", "acima"}`, e o arquivo é JSON válido (`json.dumps` sem erro, sem `NaN`).
- [ ] **Passo 2: ver falhar → implementar → ver passar.**
- [ ] **Passo 3: rodar `python scripts/gerar_previsao.py` da raiz** e abrir o JSON: tem que ter 19 / 10 / 29 / "normal" / mediana 14.
- [ ] **Passo 4: sugerir o commit:** `feat: script que gera previsao.json para o site`

### Tarefa 3: esqueleto do site + tela 1

**Arquivos:**
- Criar: `web/` (Vite + React), `web/src/App.jsx`, `web/src/Tela1.jsx`, `web/src/estilo.css`, `web/src/formato.js`

**Interfaces:**
- `formato.js`: `numeroBR(n) -> string` (`16170 → "16.170"`) e `dataBR(iso, {mes:"curto"|"longo"}) -> string` (`"2026-11-15" → "15/nov"` ou `"15 de novembro"`).
- `App.jsx` busca `/previsao.json` uma vez e passa `dados` pra `Tela1` e `Tela2`. Enquanto carrega, mostra um estado discreto. Se falhar, mostra o erro do Foco da revisão, item 2.

> ⚠️ Antes: explicar o `npm create vite@latest web -- --template react` (é o `create-react-app` moderno) e pedir o ok. É a primeira dependência JS do repo. Adicionar `web/node_modules/` e `web/dist/` ao `.gitignore`.

- [ ] **Passo 1: criar o projeto Vite, limpar o exemplo e conferir `npm run dev` abrindo uma página vazia.**
- [ ] **Passo 2: tokens de cor e fontes** em `estilo.css` (variáveis CSS com os valores das Restrições globais).
- [ ] **Passo 3: `Tela1`:**
  - menu: logo "Dengue Teresina" + "Como funciona ↗" (abre `https://dengue-teresina.streamlit.app/` com `target="_blank" rel="noopener"`);
  - à esquerda: os textos fixos, a frase de contexto com a % de março a maio, os botões "Ver a previsão da semana ↓" (rola até `#previsao`) e "Como funciona";
  - linha de números: casos em 2022 · casos em {ano} até {data} (semanas fechadas) · pico típico na semana {n};
  - à direita: um espaço reservado pro mosquito (a foto entra na Tarefa 6).
- [ ] **Passo 4: conferir no navegador** contra `mockups/tela1.html` (sem moldura e sem arcos, como diz a seção 8 da spec).
- [ ] **Passo 5: sugerir o commit:** `feat: esqueleto do site e tela de contexto`

### Tarefa 4: tela 2 (previsão) e animação do número

**Arquivos:** criar `web/src/Tela2.jsx` e `web/src/useNaTela.js`

**Interfaces:**
- `useNaTela(ref) -> boolean`: vira `true` uma vez, quando 50% do elemento entra na tela (`IntersectionObserver`).
- `Tela2({ dados })` mostra, nesta ordem:
  - o selo;
  - "Próxima semana · {dataBR longo}";
  - o número;
  - "casos previstos · provavelmente entre {min} e {max}";
  - "em {round(cobertura×10)} de cada 10 semanas testadas, o real caiu nessa faixa";
  - "Normal pra época: ~{mediana} casos";
  - o gráfico (Tarefa 5);
  - a legenda das semanas abertas;
  - a linha "o que fazer";
  - o aviso + "Dados do InfoDengue até {dados_ate} · atualizado em {atualizado_em}".

- [ ] **Passo 1: montar a tela estática** (sem animação) e conferir contra a esquerda de `mockups/tela2-calmo-surto.html`.
- [ ] **Passo 2: contagem do número** de 0 até `casos` em ~0,9 s com `requestAnimationFrame`, só depois de `useNaTela` virar `true`. Faixa, referência e aviso aparecem com fade depois. Só o valor final vai pra um `aria-live="polite"`.
- [ ] **Passo 3: `prefers-reduced-motion`** → o número final aparece direto.
- [ ] **Passo 4: aviso de previsão velha** (Foco da revisão, item 3).
- [ ] **Passo 5: conferir 3 casos** trocando o JSON à mão numa cópia temporária, sem commitar:
  - `status: "acima"` com 800 / 432 / 1248 → bate com a direita do mockup;
  - `atualizado_em` de 30 dias atrás → o aviso aparece;
  - JSON renomeado → mensagem de erro.
- [ ] **Passo 6: sugerir o commit:** `feat: tela de previsao com contagem animada`

### Tarefa 5: gráfico em SVG

**Arquivos:** criar `web/src/Grafico.jsx`

**Interfaces:** `Grafico({ recentes, previsao })`, onde `recentes` é a lista `{semana, casos, aberta}` do JSON e `previsao` traz `{semana, casos, faixa_min, faixa_max}`.

**Regras:**
- O eixo y vai de 0 até `max(casos recentes, faixa_max)`, arredondado pra cima. Só os rótulos 0 e máximo.
- Linha vertical "hoje" na última semana. Datas da primeira semana e da semana prevista embaixo.
- O trecho fechado é linha cheia. A partir da primeira semana aberta, a linha fica tracejada, encostando no último ponto fechado (igual o Streamlit faz).
- A faixa é um triângulo amarelo translúcido da última semana até a semana prevista. O ponto amarelo marca a previsão.
- Animação: a linha "se desenha" com `stroke-dashoffset` (~1,8 s) **antes** da contagem do número. Pra isso, a Tarefa 4 espera o evento de fim do gráfico ou um tempo fixo. Com reduced-motion, sem animação.

- [ ] **Passo 1: desenhar com os dados reais** (todas as 12 semanas abertas → tudo tracejado).
- [ ] **Passo 2: testar o caso misto** (Foco da revisão, item 4) com um JSON temporário com as 6 primeiras semanas `aberta: false`. A linha cheia vira tracejada sem buraco no meio.
- [ ] **Passo 3: animação de desenho e encaixe no tempo da Tarefa 4.**
- [ ] **Passo 4: sugerir o commit:** `feat: grafico das ultimas semanas com faixa da previsao`

### Tarefa 6: foto do mosquito, celular e acessibilidade

**Arquivos:** criar `web/public/mosquito.webp` e modificar `Tela1.jsx` e `estilo.css`

- [ ] **Passo 1: procurar uma foto de domínio público do *Aedes aegypti*** (CDC/Wikimedia Commons). **Mostrar ao João o link, o tamanho e a licença e pedir o ok antes de baixar.**
- [ ] **Passo 2: recortar o fundo e passar pra cinza.** Explicar a ferramenta antes; se precisar instalar algo, pedir o ok. Salvar em webp com até ~200 KB. `alt="Mosquito Aedes aegypti, transmissor da dengue"`. Crédito no rodapé.
- [ ] **Passo 3: celular (≤ 700px):**
  - as telas empilham;
  - título e número com `clamp()`;
  - o mosquito fica pequeno, acima do título;
  - **o número da previsão aparece sem rolar** na tela 2.
  
  Conferir em 375px e 1280px.
- [ ] **Passo 4: navegação só por teclado** (Tab passa pelos botões, com foco visível) e contraste dos textos de 13px.
- [ ] **Passo 5: sugerir o commit:** `feat: foto do mosquito e ajustes para celular`

### Tarefa 7: revisão de design, deploy e links

- [ ] **Passo 1: rodar `/impeccable audit` e `/impeccable polish`** no site rodando e corrigir o que o João aprovar.
- [ ] **Passo 2: deploy na Vercel** (o João cria a conta e conecta o repo, com pasta raiz `web/`, build `npm run build` e saída `dist`). Conferir o site publicado em 375px e 1280px.
- [ ] **Passo 3: README:**
  - link do site novo;
  - uma linha de como atualizar: rodar os notebooks e depois `python scripts/gerar_previsao.py`, e commitar o JSON.
- [ ] **Passo 4: sugerir o commit:** `docs: link do site e como atualizar a previsao`

**Fora deste plano (fase 2):** GitHub Actions semanal; atualizar o card do portfólio.
