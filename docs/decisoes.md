# Decisões e conferências

Registro do porquê de cada escolha do projeto e do que eu conferi nos dados antes de decidir. O resumo fica no [README](../README.md).

## O problema

**Horizonte.** Começo prevendo uma semana à frente, que é mais simples e me deixa validar o pipeline de ponta a ponta. Depois a ideia é chegar a quatro semanas, com um modelo para cada horizonte.

**Alvo.** As notificações de dengue chegam atrasadas, então as semanas mais recentes aparecem com menos casos do que realmente tiveram. Por isso o alvo é o `casos_est`, a estimativa do InfoDengue que corrige esse atraso. Nas semanas antigas, ele é igual ao número notificado.

## Casos (InfoDengue)

**Semanas em aberto: 20.** O InfoDengue só corrige as 10 semanas mais recentes (`casos_est` maior que `casos`). Mas comparei o download com dados até 04/10/2026 com o download com dados até 11/10/2026, e os números mudaram nas 20 semanas mais recentes, inclusive em semanas que o InfoDengue já tratava como fechadas: a de 28/06/2026 foi de 292 para 335 casos. Essas 20 semanas ficam marcadas na coluna `semana_aberta`, fora do treino e da avaliação, mas continuam como entrada na previsão. É uma comparação só; se outro download mostrar revisão além de 20 semanas, o número muda.

**Colunas que ficaram de fora.** Fiquei só com `data_iniSE`, `SE`, `casos` e `casos_est`. Indicadores como o `Rt` e o nível de alerta são calculados pelo InfoDengue a partir dos próprios casos e recalculados por versões mais novas do modelo deles. Usar isso como entrada seria dar ao modelo uma dica da resposta. O clima do InfoDengue também saiu, porque só existe a partir de junho de 2023 e não tem chuva.

## Clima

**Plano inicial: estação automática A312 do INMET** (aeroporto de Teresina). É medição real e oficial, de hora em hora, com chuva, temperatura e umidade.

**Os buracos da A312 eram grandes demais para média.** Medi a cobertura ano a ano: a estação ficou parada de julho de 2024 a janeiro de 2026 (cerca de 18 meses) e em boa parte de 2020, e em 2022, o ano do surto, faltam 66% das horas de janeiro e 51% de fevereiro. Preencher isso com média seria inventar clima justamente no fim da série, onde fica o teste do modelo. Por isso entrou o ERA5, e o plano passou a ser usar a A312 onde ela mediu e o ERA5 nos buracos.

**Decisão final: ERA5 no período todo; a A312 fica só para conferência.** Antes de emendar, comparei as duas nas 451 semanas em que a A312 mediu as 168 horas. Temperatura e umidade batem bem: correlação de 0,92 a 0,95, com o ERA5 só um pouco acima (+0,6 °C na média, +2 pontos de umidade). A temperatura mínima é a mais fraca (correlação 0,60, ERA5 +1,0 °C). A chuva bate na média geral, mas a relação muda de ano para ano: o ERA5 choveu 85% a mais que a estação em 2015, quase igual em 2017–2018 e 32% a menos em 2022. Emendar as duas criaria degraus de clima que seriam só troca de instrumento, e não existe um fator único para corrigir a chuva (calcular um usando semanas que vão cair no teste ainda seria vazamento de informação). Com uma régua só de 2015 a 2026, uma mudança no clima do modelo é mudança no clima. A A312 continua na tabela, com sufixo `_a312`, para a análise exploratória.

**ERA5 puro, e não o padrão do Open-Meteo.** O padrão (`best_match`) troca de modelo no meio da série, e o motivo de usar o ERA5 é justamente ter o mesmo instrumento em 2015 e em 2026. O custo é a resolução: a grade de ~25 km suaviza a chuva de pancada (a maior chuva numa hora foi 68,6 mm na A312 e 31,7 mm no ERA5).

**Só três variáveis.** Chuva, temperatura e umidade: as ligadas ao ciclo do mosquito e as que existem nas duas fontes.

**Agregação semanal.** Por semana epidemiológica, de domingo a sábado no horário de Teresina (os dados vêm em UTC). Chuva é somada; temperatura vira média, mínima e máxima; umidade vira média. As duas fontes passam pela mesma função. Cada semana guarda quantas horas foram medidas, porque uma soma de chuva com metade das horas faltando parece uma semana seca.

## Dados brutos

**Dado bruto congelado.** A API do InfoDengue revisa os números com o tempo, então guardo uma cópia em `data/raw/` e não mexo mais nela. Tudo o que é tratado vai para `data/processed/`, sempre gerado pelos notebooks.

**ZIPs do INMET fora do Git.** Cada ZIP anual tem cerca de 100 MB, com as ~500 estações do Brasil. Só o CSV da A312 de cada ano é extraído por código, sem alteração, e versionado (~9 MB no total). Assim o repositório roda sem baixar nada.

## Conferências nos dados

**A chuva de 2015 parecia baixa demais.** A A312 deu 535,6 mm no ano, contra uma média histórica de cerca de 1.356 mm. Conferi com os boletins do próprio INMET: abril/2015 tem 225,0 mm no boletim e 222,4 mm no meu cálculo, e novembro/2015 tem 0,0 mm nos dois. O arquivo é fiel ao registro oficial, e 2015 foi mesmo seco (El Niño). Mas o ERA5 deu 992 mm no mesmo ano, quase toda a diferença em janeiro a março. Na comparação semana a semana, 2015 e 2016 são justamente os anos em que a A312 fica mais abaixo do ERA5. Não dá para saber, só com esses dados, qual das duas está certa nesses anos; pode ter sido o pluviômetro medindo a menos.

**O INMET mudou o formato em 2019.** Até 2018 a data vem como `2015-01-01` e a hora como `00:00`; a partir de 2019, `2019/01/01` e `0000 UTC`, com outro nome de coluna. A leitura padroniza os dois formatos e confere, em todos os anos, que as colunas lidas pela posição são mesmo chuva, temperatura e umidade.

**O ZIP de 2026 tem dois arquivos da A312** (até 31/08 e até 30/09). Comparei linha por linha: janeiro a agosto é idêntico nos dois. Uso só o mais recente, escolhido pela data de fim e não pelo nome (como texto, "30-09" vem antes de "31-08"), e confiro que nenhuma hora aparece duas vezes.
