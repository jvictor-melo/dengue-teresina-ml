import { useEffect, useState } from 'react'

// Vira true uma única vez, quando metade do elemento aparece na tela
// (IntersectionObserver = o navegador avisa quando o elemento entra na área visível)
export default function useNaTela(ref) {
  const [naTela, setNaTela] = useState(false)

  useEffect(() => {
    const elemento = ref.current
    if (!elemento || naTela) return

    const observador = new IntersectionObserver(
      (entradas) => {
        if (entradas[0].isIntersecting) {
          setNaTela(true)
          observador.disconnect()
        }
      },
      { threshold: 0.5 },
    )
    observador.observe(elemento)
    return () => observador.disconnect()
  }, [ref, naTela])

  return naTela
}
