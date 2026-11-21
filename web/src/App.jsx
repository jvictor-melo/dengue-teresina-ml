import { useEffect, useState } from 'react'
import Tela1 from './Tela1.jsx'
import Tela2 from './Tela2.jsx'

export default function App() {
  // Os três estados possíveis: carregando, deu erro, ou com os dados
  const [dados, setDados] = useState(null)
  const [erro, setErro] = useState(false)

  useEffect(() => {
    // O previsao.json é gerado pelo scripts/gerar_previsao.py e fica em web/public/
    // no-cache: confere com o servidor se o arquivo mudou, pra ninguém ver a previsão da semana passada
    fetch('/previsao.json', { cache: 'no-cache' })
      .then((resposta) => {
        if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`)
        return resposta.json()
      })
      .then(setDados)
      .catch(() => setErro(true))
  }, [])

  // Link direto pra #previsao: a seção só existe depois que o JSON chega, então rola nessa hora
  useEffect(() => {
    if (dados && window.location.hash) {
      document.querySelector(window.location.hash)?.scrollIntoView()
    }
  }, [dados])

  if (erro) {
    return (
      <p className="aviso-carga" role="alert">
        Não foi possível carregar a previsão agora. Recarregue a página em alguns instantes.
      </p>
    )
  }

  if (!dados) {
    return <p className="aviso-carga">Carregando a previsão…</p>
  }

  return (
    <>
      <Tela1 dados={dados} />
      <main>
        <Tela2 dados={dados} />
      </main>
      <footer className="rodape pagina">
        <p>
          Casos: <a href="https://info.dengue.mat.br/" target="_blank" rel="noopener">InfoDengue</a>.
          Foto do mosquito: James Gathany, CDC (domínio público).
        </p>
        <p>
          Código e metodologia no{' '}
          <a href="https://github.com/jvictor-melo/dengue-teresina-ml" target="_blank" rel="noopener">GitHub</a>.
        </p>
      </footer>
    </>
  )
}
