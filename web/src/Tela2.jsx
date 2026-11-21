import { useEffect, useRef, useState } from 'react'
import { dataBR, numeroBR } from './formato.js'
import Grafico from './Grafico.jsx'
import useNaTela from './useNaTela.js'

// Texto do selo pra cada status que vem do JSON
const SELOS = {
  abaixo: 'Abaixo do normal pra época',
  normal: 'Normal pra época',
  acima: 'Acima do normal pra época',
}

const DURACAO_GRAFICO = 1400 // ms (igual à transição da .cortina no CSS)
const DURACAO_CONTAGEM = 900 // ms
const DIAS_PRA_FICAR_VELHA = 14

function prefereSemMovimento() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

// Quantos dias se passaram desde uma data "AAAA-MM-DD"
function diasDesde(iso) {
  const [ano, mes, dia] = iso.split('-').map(Number)
  const data = new Date(ano, mes - 1, dia)
  return Math.floor((Date.now() - data.getTime()) / 86_400_000)
}

export default function Tela2({ dados }) {
  const p = dados.previsao
  // O gatilho é o número, não a seção inteira: num celular deitado a seção é mais alta que duas telas,
  // e "metade da seção visível" nunca aconteceria (o número ficaria parado no 0)
  const ref = useRef(null)
  const naTela = useNaTela(ref)
  const semMovimento = prefereSemMovimento()

  // O número começa em 0 e conta até a previsão quando a tela aparece
  const [mostrado, setMostrado] = useState(semMovimento ? p.casos : 0)
  const [terminou, setTerminou] = useState(semMovimento)

  useEffect(() => {
    if (!naTela || semMovimento) return
    let quadro
    let inicio

    // Ordem da animação: primeiro o gráfico se desenha (CSS), depois o número conta
    const espera = setTimeout(() => {
      inicio = performance.now()
      quadro = requestAnimationFrame(passo)
    }, DURACAO_GRAFICO)

    function passo(agora) {
      const progresso = Math.min((agora - inicio) / DURACAO_CONTAGEM, 1)
      // ease-out: começa rápido e freia no final
      const suave = 1 - Math.pow(1 - progresso, 3)
      setMostrado(Math.round(p.casos * suave))
      if (progresso < 1) {
        quadro = requestAnimationFrame(passo)
      } else {
        setTerminou(true)
      }
    }
    return () => {
      clearTimeout(espera)
      cancelAnimationFrame(quadro)
    }
  }, [naTela, semMovimento, p.casos])

  const diasParado = diasDesde(dados.atualizado_em)
  const estaVelha = diasParado > DIAS_PRA_FICAR_VELHA

  return (
    <section id="previsao" className="tela2 pagina" aria-labelledby="titulo-previsao">
      <div className={`previsao ${naTela || semMovimento ? 'desenhando' : ''} ${terminou ? 'pronta' : ''}`}>
        <div className="previsao-numero">
          <p className={`selo selo-${p.status}`}>{SELOS[p.status]}</p>
          <h2 id="titulo-previsao" className="semana">Próxima semana, {dataBR(p.semana)}</h2>

          {/* aria-hidden no número que conta; o leitor de tela recebe só o valor final, logo abaixo */}
          <p className="casos" aria-hidden="true" ref={ref}>{numeroBR(mostrado)}</p>
          <p className="so-leitor" aria-live="polite">{terminou ? `${numeroBR(p.casos)} casos previstos` : ''}</p>

          <p className="faixa revela">
            casos previstos, provavelmente entre <strong>{numeroBR(p.faixa_min)} e {numeroBR(p.faixa_max)}</strong>
            <span className="faixa-explica">
              Em {Math.round(p.cobertura * 10)} de cada 10 semanas testadas, o número real caiu nessa faixa.
            </span>
          </p>
          <p className="referencia revela">
            Normal pra época: <strong>cerca de {numeroBR(p.mediana_epoca)} casos</strong>
          </p>
        </div>

        <Grafico recentes={dados.recentes} previsao={p} />
      </div>

      <div className="rodape-previsao">
        <p className="fazer">
          <strong>Pra evitar o mosquito:</strong> não deixe água parada em vasos, pneus e caixas d'água.
        </p>
        <p className={`aviso ${estaVelha ? 'aviso-velha' : ''}`}>
          Previsão de um modelo estatístico, não é dado oficial. Dados do InfoDengue até {dataBR(dados.dados_ate)},
          atualizado em {dataBR(dados.atualizado_em)}
          {estaVelha ? `, há ${diasParado} dias. Pode haver números mais recentes.` : '.'}
        </p>
      </div>
    </section>
  )
}
