import { dataBR, numeroBR } from './formato.js'

// Tamanho interno do desenho (o SVG estica pra largura da tela mantendo a proporção)
const LARGURA = 600
const ALTURA = 300
const MARGEM = { esquerda: 44, direita: 16, topo: 20, baixo: 36 }

// Arredonda o topo do eixo pra um número "redondo" (29 → 30, 1248 → 1300)
function topoRedondo(valor) {
  const passo = valor <= 50 ? 10 : valor <= 200 ? 25 : valor <= 1000 ? 100 : 250
  return Math.ceil(valor / passo) * passo
}

// Transforma uma lista de pontos {x, y} no texto que o <path> entende ("M x y L x y ...")
function caminho(pontos) {
  return pontos.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
}

export default function Grafico({ recentes, previsao }) {
  const maior = Math.max(...recentes.map((s) => s.casos), previsao.faixa_max)
  const topo = topoRedondo(maior)

  // Escalas: semana (posição na lista) → x, casos → y (y cresce pra baixo no SVG, por isso o "1 -")
  const total = recentes.length // a previsão fica na posição "total", logo depois da última semana
  const x = (i) => MARGEM.esquerda + (i / total) * (LARGURA - MARGEM.esquerda - MARGEM.direita)
  const y = (casos) => MARGEM.topo + (1 - casos / topo) * (ALTURA - MARGEM.topo - MARGEM.baixo)

  const pontos = recentes.map((s, i) => ({ x: x(i), y: y(s.casos), aberta: s.aberta }))

  // Linha cheia até a última semana fechada; tracejada daí em diante (encostando no último ponto fechado)
  const primeiraAberta = pontos.findIndex((p) => p.aberta)
  const fechados = primeiraAberta === -1 ? pontos : pontos.slice(0, primeiraAberta)
  const abertos = primeiraAberta === -1 ? [] : pontos.slice(Math.max(0, primeiraAberta - 1))

  const ultimo = pontos[pontos.length - 1]
  const xPrevisao = x(total)
  const chao = y(0)

  const resumo = `Casos por semana de ${dataBR(recentes[0].semana)} a ${dataBR(recentes[total - 1].semana)}, ` +
    `terminando em ${numeroBR(recentes[total - 1].casos)}. Previsão de ${numeroBR(previsao.casos)} casos ` +
    `para ${dataBR(previsao.semana)}, entre ${numeroBR(previsao.faixa_min)} e ${numeroBR(previsao.faixa_max)}.`

  return (
    <figure className="grafico">
      <svg viewBox={`0 0 ${LARGURA} ${ALTURA}`} role="img" aria-label={resumo}>
        <defs>
          {/* A "cortina" que vai abrindo da esquerda pra direita: é ela que faz o gráfico se desenhar */}
          <clipPath id="cortina">
            <rect className="cortina" x="0" y="0" width={LARGURA} height={ALTURA} />
          </clipPath>
        </defs>

        {/* Eixo: só o zero e o topo */}
        <line className="g-base" x1={MARGEM.esquerda} x2={LARGURA - MARGEM.direita} y1={chao} y2={chao} />
        <text className="g-rotulo" x={MARGEM.esquerda - 10} y={chao + 4} textAnchor="end">0</text>
        <text className="g-rotulo" x={MARGEM.esquerda - 10} y={MARGEM.topo + 4} textAnchor="end">{numeroBR(topo)}</text>

        {/* "Hoje": a última semana com dado */}
        <line className="g-hoje" x1={ultimo.x} x2={ultimo.x} y1={MARGEM.topo} y2={chao} />
        <text className="g-rotulo" x={ultimo.x - 6} y={MARGEM.topo + 4} textAnchor="end">hoje</text>

        <g clipPath="url(#cortina)">
          {/* Faixa da previsão: um leque da última semana até a semana prevista */}
          <path
            className="g-faixa"
            d={`M${ultimo.x} ${ultimo.y} L${xPrevisao} ${y(previsao.faixa_max)} L${xPrevisao} ${y(previsao.faixa_min)} Z`}
          />
          {fechados.length > 1 && <path className="g-linha" d={caminho(fechados)} />}
          {abertos.length > 1 && <path className="g-linha g-linha-aberta" d={caminho(abertos)} />}
          <line className="g-previsao" x1={ultimo.x} y1={ultimo.y} x2={xPrevisao} y2={y(previsao.casos)} />
          <circle className="g-ponto" cx={xPrevisao} cy={y(previsao.casos)} r="6" />
        </g>

        {/* Datas: a primeira semana e a semana prevista */}
        <text className="g-rotulo" x={x(0)} y={ALTURA - 8} textAnchor="start">{dataBR(recentes[0].semana, 'curto')}</text>
        <text className="g-rotulo g-rotulo-forte" x={xPrevisao} y={ALTURA - 8} textAnchor="end">{dataBR(previsao.semana, 'curto')}</text>
      </svg>

      {abertos.length > 0 && (
        <figcaption className="g-legenda">
          <svg className="g-amostra" viewBox="0 0 24 4" aria-hidden="true">
            <line x1="0" y1="2" x2="24" y2="2" />
          </svg>
          semanas ainda sendo atualizadas (os números costumam subir)
        </figcaption>
      )}
    </figure>
  )
}
