# Site "Dengue em Teresina": design

Data: 20/11/2026 · Status: rascunho para aprovação do João

## 1. Intenção

Um site próprio, de uma página, que **informa** quem mora em Teresina (ou quem chega pelo portfólio do João) sobre a dengue na cidade e mostra **quantos casos o modelo prevê para a semana que vem**. A pessoa deve sair pensando "então vai ter X casos de dengue".

O site **não é uma vitrine do João**: fala da cidade, não dele nem do modelo. Quem quiser entender o modelo é mandado pro Streamlit, que já está no ar em https://dengue-teresina.streamlit.app/.

## 2. Objetivos, não-objetivos e anti-objetivos

**Objetivos**
- Uma página com duas telas: contexto da dengue em Teresina → previsão da próxima semana.
- Visual próprio, moderno, preto e amarelo.
- Nenhum número digitado à mão: tudo sai dos dados e do modelo do projeto.
- O número do site é **o mesmo** do Streamlit.

**Não-objetivos (agora)**
- Atualização automática semanal (fica pra uma fase 2, com GitHub Actions).
- Explicar a avaliação do modelo (isso é o Streamlit).
- Previsão de 1 a 4 semanas (versão 2 do modelo).

**Anti-objetivos (seria fracasso mesmo funcionando)**
- Passar mais certeza do que o modelo tem (número sem faixa, sem aviso).
- Soar alarmista numa semana calma.
- Parecer ferramenta oficial de saúde.
- Mostrar previsão velha sem deixar claro de quando ela é.
- Ficar com cara de "olha o que eu fiz" em vez de informar.

## 3. Restrições

- `data/raw/` é intocável. O site só lê o que já está em `data/processed/` e `models/`.
- O site e o Streamlit precisam calcular a previsão **com o mesmo código** (senão divergem).
- Sem servidor pra manter: site estático.
- O João não commita nada por mim; tudo fica pra ele revisar e commitar.

## 4. Abordagens consideradas

| | Como | Prós | Contras |
|---|---|---|---|
| **A (escolhida)** | Site em `web/` dentro do repo; script Python gera `previsao.json`; deploy estático | Simples, um repo, mesmos números do Streamlit | Atualização manual (como o Streamlit hoje) |
| B | Igual A + GitHub Actions toda semana | Sempre atualizado | Notebooks 01/02 teriam que virar script agora; mais risco e atraso |
| C | O navegador baixa o InfoDengue e faz a conta em JS | Sempre fresco, sem robô | Lógica duplicada em Python e JS; CORS do InfoDengue desconhecido |

**Escolha do João: A agora, B como fase 2.**

## 5. O que o João decidiu (como decidido)

### Fluxo
- **Duas telas.** A tela 1 tem um botão **"Ver a previsão da semana ↓"** que desce até a tela 2. Rolar também funciona.
- Na tela 2 a animação **começa sozinha** quando ela entra na tela (a pessoa não aperta nada pra animar).

### Identidade visual
- **Identidade própria**, independente do portfólio.
- Estrutura inspirada na referência "Multidisciplinary designer" (Ada Rennick): moldura com arcos sutis atrás, cartão por cima com cantos arredondados, menu em pílula flutuando no topo, botões em pílula (um cheio, um com contorno), título serifado enorme.
- **Versão escura:** fundo preto/grafite, texto creme, **amarelo só nos destaques** (número da previsão, gráfico, botão principal, marca-texto na palavra "dengue").
- **Tela 1:** texto **à esquerda**, **foto do mosquito da dengue à direita, recortada (sem fundo) e em tons de cinza**.

### Conteúdo
**Tela 1**
- Linha pequena: "Todo ano, entre março e maio."
- Título: "A temporada da **dengue**" ("dengue" com marca-texto amarelo).
- Frase de contexto: "62% dos casos de Teresina chegam nesses três meses. Alguns anos são calmos; outros viram surto."
- Botões: "Ver a previsão da semana ↓" (cheio) e "Como funciona" (contorno).
- Linha com 3 números: % dos casos entre março e maio · casos em 2022 · casos em 2026 até a última semana fechada.

**Tela 2**
- Selo de status (ex.: "● Semana tranquila").
- "Próxima semana · {data}".
- Número da previsão, gigante, em amarelo, contando de 0 até o valor.
- "casos previstos · provavelmente entre {mín} e {máx}".
- Gráfico das últimas semanas + previsão com a faixa, desenhando-se da esquerda pra direita.
- Aviso discreto: "Previsão de um modelo estatístico, não é dado oficial. As últimas semanas ainda estão sendo atualizadas."

Mockups de referência (rascunhos de estrutura e cor, não visual final), nesta pasta:
- `mockups/tela1.html`: tela 1 (texto à esquerda, mosquito à direita; o mosquito é um desenho provisório).
- `mockups/estilo-preto-amarelo.html`: a **versão B (escura)** é a escolhida; dela vem a tela 2.

**Decisões do Claude pra fechar lacunas (o João pode corrigir):**
- **"Como funciona"** abre o Streamlit (https://dengue-teresina.streamlit.app/) numa aba nova. Não tem seção nem modal no site.
- **Textos com números** (o "62%" da frase, os 3 números da linha) saem do JSON. Porcentagem arredondada pra inteiro; "entre março e maio" fica fixo no texto.

## 6. Como funciona por dentro (proposta do Claude, aprovada na escolha "A")

```
data/processed/dengue_clima_semanal.csv ─┐
models/modelo_final.joblib + .json ──────┼─► scripts/gerar_previsao.py ─► web/public/previsao.json ─► site (React)
src/features.py, src/avaliacao.py ───────┘
```

### 6.1 Lógica de previsão compartilhada
Hoje a conta da previsão está escrita dentro de `app/app.py`. Ela vai para uma função em `src/` (ex.: `prever_proxima_semana(dados, modelo, info)` em `src/previsao.py`), e **o Streamlit e o script passam a chamar a mesma função**. Assim os dois nunca divergem.

Escopo da mudança (decisão do Claude): a função devolve a previsão, a faixa e o status. As 12 semanas recentes saem de outra função pequena em `src/`, que o Streamlit também passa a usar. O Streamlit **tem que continuar mostrando os mesmos números** de antes. Conferir com `AppTest` antes e depois. Os números de contexto da tela 1 ficam só no script, porque o Streamlit não mostra esses números.

### 6.2 Script `scripts/gerar_previsao.py`
Roda da raiz do projeto, depois de atualizar os dados como o João já faz hoje. Lê os dados tratados e o modelo e escreve `web/public/previsao.json`. Não baixa nada e não mexe em `data/`.

### 6.3 Formato do `previsao.json`
```json
{
  "atualizado_em": "2026-11-18",
  "dados_ate": "2026-11-08",
  "previsao": {
    "semana": "2026-11-15",
    "casos": 19,
    "faixa_min": 10,
    "faixa_max": 29,
    "status": "tranquila"
  },
  "recentes": [
    {"semana": "2026-08-23", "casos": 41, "aberta": true}
  ],
  "contexto": {
    "pct_mar_mai": 62.4,
    "casos_2022": 16170,
    "ano_atual": 2026,
    "casos_ano_atual_fechados": 9263,
    "ultima_semana_fechada": "2026-06-21"
  }
}
```
- `recentes`: últimas 12 semanas de `casos_est` (a mesma coluna e a mesma janela do gráfico do Streamlit), com `aberta` vindo de `semana_aberta`. Semanas abertas aparecem tracejadas no gráfico.
- Números de contexto calculados só com semanas fechadas, do mesmo jeito da EDA.

### 6.4 Site `web/`
- **Vite + React** (o João é forte em React). Sem biblioteca de gráfico: o gráfico é um SVG desenhado à mão com os 12 pontos + previsão, o que deixa a animação de "desenhar a linha" simples.
- Animações: CSS + `IntersectionObserver` + `requestAnimationFrame` (mesmas técnicas do portfólio). Se o sistema pedir **reduzir movimento**, tudo aparece pronto, sem animar.
- Fontes: Instrument Serif (títulos e números) + Manrope (texto), via Google Fonts.
- Celular: as duas telas empilham; o mosquito vai pra cima ou some, e o título diminui.
- A data "dados até" aparece visível na tela 2, pra ninguém confundir previsão velha com atual.

### 6.5 Hospedagem
**Vercel**, ligada ao repositório, com a pasta raiz `web/`. Cada push publica sozinho. (A conta na Vercel o João cria.)

## 7. O que fica pro implementador decidir
- Estrutura de componentes do React.
- Tempos exatos das animações.
- Ajustes finos de espaçamento e responsividade.
- Formato dos números em português (vírgula, ponto de milhar).

## 8. Decisões tomadas depois da revisão

### Selo de status (João escolheu A: comparar com o normal da época)
Compara a previsão com o **ano típico** daquela semana (mediana de `casos_est` daquela semana do ano, só semanas fechadas, como o Streamlit já calcula).

Regra pra margem (proposta do Claude, usa a própria faixa de 80% do modelo em vez de um número inventado):
- **"Abaixo do normal pra época"**: o topo da faixa fica abaixo da mediana.
- **"Acima do normal pra época"**: o piso da faixa fica acima da mediana.
- **"Normal pra época"**: a mediana cai dentro da faixa.

Valores no JSON: `status` = `"abaixo"`, `"normal"` ou `"acima"`, e `mediana_epoca` junto, pra conferir. Cor do ponto do selo: verde (abaixo), amarelo (normal), vermelho (acima).

**Cores do selo (correção do impeccable, aprovada pelo João):** tudo dentro da paleta, sem verde e sem vermelho, e o texto do selo sempre diz o estado (não depende só da cor):
- abaixo → contorno creme;
- normal → contorno amarelo;
- acima → amarelo cheio com texto preto.

> Com os dados de hoje, a semana de 15/11 tem previsão 19 (faixa 10–29) e normal pra época ~14 → selo **"Normal pra época"** (não "tranquila", como nos primeiros rascunhos).

### Correções da crítica do impeccable (20/11/2026, aprovadas pelo João)
Valem por cima do que está na seção 5 quando houver conflito.
- **Sem moldura externa e sem arcos.** O cartão escuro fica direto no fundo. O menu fica só **logo + "Como funciona"** (que abre o Streamlit numa nova aba e mostra o ícone ↗). Visual escuro, título serifado e pílulas continuam.
- **Tela 2, linha de referência:** "Normal pra época: ~X casos" logo abaixo da faixa (a mesma mediana do selo; vai no JSON como `mediana_epoca`).
- **Tela 2, faixa explicada:** embaixo da faixa, "em 8 de cada 10 semanas testadas, o real caiu nessa faixa" (texto gerado a partir de `cobertura_janela_movel` no JSON).
- **Gráfico legível:** linha vertical "hoje" na última semana com dado, data da primeira semana e da semana prevista, mínimo (0) e máximo no eixo, **semanas abertas tracejadas** com a legenda "semanas ainda sendo atualizadas (os números costumam subir)" e a faixa da previsão bem visível. Obs.: hoje as 12 semanas do gráfico são todas abertas, então a linha inteira sai tracejada.
- **Data dos dados sempre visível:** "Dados do InfoDengue até {dados_ate} · atualizado em {atualizado_em}". Na tela 1, o número de 2026 vira "em 2026 até {ultima_semana_fechada} (semanas fechadas)".
- **Aviso e legendas maiores:** no mínimo 13px, sem transparência que derrube o contraste.
- **Linha "o que fazer":** "Pra evitar o mosquito: não deixe água parada em vasos, pneus e caixas d'água."
- **Linha de números da tela 1:** sai o 62% repetido (já está na frase). Fica: casos em 2022 · casos em 2026 até a última semana fechada, e mais um número a definir na implementação (ex.: semana do pico típico).
- **Estado de surto testado:** mockup `mockups/tela2-calmo-surto.html` (direita = exemplo inventado de abril, 800 casos, "Acima do normal pra época").
- **Acessibilidade:** foto do mosquito com `alt` descritivo; a contagem animada só anuncia o valor final pro leitor de tela; `prefers-reduced-motion` mostra tudo pronto.

### Foto do mosquito (João pediu pro Claude arrumar)
Na implementação, o Claude procura uma foto **de domínio público** do *Aedes aegypti* (por exemplo, do CDC na Wikimedia Commons), mostra o link e o tamanho e **pede o ok antes de baixar**. Depois recorta o fundo, deixa em cinza e coloca o crédito no rodapé do site. Se não achar uma boa, volta pro João.
