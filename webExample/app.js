async function loadState() {
  const response = await fetch('./data/state.json?_=' + Date.now())
  const state = await response.json()
  const boards = document.getElementById('boards')
  const groups = [
    ['resultados', 'Resultados'],
    ['certificados', 'Certificados'],
    ['fechas', 'Fechas'],
    ['evaluaciones', 'Evaluaciones'],
    ['notas', 'Notas'],
  ]

  boards.innerHTML = groups
    .map(([key, label]) => {
      const pendientes = state.pendientes[key] || []
      const procesados = state[key] || []
      return `
        <article class="card">
          <h2>${label}</h2>
          <p>Pendientes: ${pendientes.length}</p>
          <p>Procesados: ${procesados.length}</p>
          <details>
            <summary>Ver detalle</summary>
            <pre>${JSON.stringify({ pendientes, procesados }, null, 2)}</pre>
          </details>
        </article>
      `
    })
    .join('')
}

loadState()
setInterval(loadState, 3000)
