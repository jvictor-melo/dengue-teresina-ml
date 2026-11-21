// Formatação no jeito brasileiro (16170 → "16.170", "2026-11-15" → "15 de novembro")

const MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

export function numeroBR(n) {
  return n.toLocaleString('pt-BR')
}

// As datas do JSON são "AAAA-MM-DD". Separo na mão pra não cair no fuso horário
// (new Date("2026-11-15") vira meia-noite UTC, que em Teresina ainda é dia 14)
export function dataBR(iso, formato = 'longo') {
  const [, mes, dia] = iso.split('-').map(Number)
  if (formato === 'curto') {
    return `${dia}/${MESES[mes - 1].slice(0, 3)}`
  }
  return `${dia} de ${MESES[mes - 1]}`
}
