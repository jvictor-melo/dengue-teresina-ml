import { dataBR, numeroBR } from './formato.js'
import { IconeDescer, IconeSaida } from './Icones.jsx'

export const LINK_STREAMLIT = 'https://dengue-teresina.streamlit.app/'

// Semana do ano → mês aproximado, só pra legenda do pico ("meados de abril")
function mesDaSemana(semana) {
  const meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
  const indice = Math.min(11, Math.floor(((semana - 1) * 7 + 3) / 30.44))
  return meses[indice]
}

export default function Tela1({ dados }) {
  const c = dados.contexto

  return (
    <header className="tela1 pagina">
      <nav className="topo" aria-label="Principal">
        <a className="marca" href="#">Dengue em Teresina</a>
        <a className="link-topo" href={LINK_STREAMLIT} target="_blank" rel="noopener">
          Como funciona <IconeSaida />
        </a>
      </nav>

      <div className="abertura">
        <div>
          <h1 className="titulo">
            A temporada da <span className="marca-texto">dengue</span>
          </h1>
          <p className="contexto">
            Todo ano, entre março e maio, Teresina recebe <strong>{numeroBR(c.pct_mar_mai)}% dos casos</strong> de
            dengue. Alguns anos são calmos; outros viram surto.
          </p>
          <div className="acoes">
            <a className="botao botao-cheio" href="#previsao">
              Ver a previsão da semana <IconeDescer />
            </a>
            <a className="botao botao-contorno" href={LINK_STREAMLIT} target="_blank" rel="noopener">
              Como funciona <IconeSaida />
            </a>
          </div>
        </div>

        <img
          className="mosquito"
          src="/mosquito.webp"
          width="1200"
          height="779"
          alt="Mosquito Aedes aegypti, transmissor da dengue, visto de lado"
          fetchPriority="high"
        />
      </div>

      <dl className="numeros">
        <div>
          <dt className="numero-legenda">casos em 2022, o maior surto desde 2015</dt>
          <dd className="numero-valor">{numeroBR(c.casos_2022)}</dd>
        </div>
        <div>
          <dt className="numero-legenda">casos em {c.ano_atual} até {dataBR(c.ultima_semana_fechada)}, contando só as semanas já fechadas</dt>
          <dd className="numero-valor">{numeroBR(c.casos_ano_atual_fechados)}</dd>
        </div>
        <div>
          <dt className="numero-legenda">o pico de um ano comum, em {mesDaSemana(c.semana_pico_tipico)}</dt>
          <dd className="numero-valor">Semana {c.semana_pico_tipico}</dd>
        </div>
      </dl>
    </header>
  )
}
