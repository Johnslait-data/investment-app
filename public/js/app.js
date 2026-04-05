// Cargar portafolio al iniciar
document.addEventListener('DOMContentLoaded', () => {
  cargarPortafolio();
  cargarTransacciones();
});

// Cargar portafolio
async function cargarPortafolio() {
  try {
    const response = await fetch('/api/portfolio');
    if (!response.ok) throw new Error('Portfolio API error');

    const portfolio = await response.json();

    // Actualizar resumen (solo si los elementos existen)
    const elementos = ['capitalInicial', 'aporteBimestral', 'horizonte', 'metodologia'];

    if (document.getElementById('capitalInicial')) {
      document.getElementById('capitalInicial').textContent = formatearMoneda(portfolio.meta.capitalInicial);
    }
    if (document.getElementById('aporteBimestral')) {
      document.getElementById('aporteBimestral').textContent = formatearMoneda(portfolio.meta.aporteBimestral);
    }
    if (document.getElementById('horizonte')) {
      document.getElementById('horizonte').textContent = portfolio.meta.horizonteTiempo;
    }
    if (document.getElementById('metodologia')) {
      document.getElementById('metodologia').textContent = portfolio.meta.metodologia.split(' - ')[1];
    }

    // Actualizar activos (solo los que existen en el DOM)
    const activos = ['GEB', 'TERPEL', 'TITULARIZADORA'];
    activos.forEach(ticker => {
      const activo = portfolio.activos[ticker];
      if (activo) {
        const precioEl = document.getElementById(`${ticker}-precio`);
        if (precioEl) precioEl.textContent = formatearMoneda(activo.precioActual);

        const montoEl = document.getElementById(`${ticker}-monto`);
        if (montoEl) montoEl.textContent = formatearMoneda(activo.monto);

        const pctEl = document.getElementById(`${ticker}-porcentaje`);
        if (pctEl) pctEl.textContent = activo.porcentaje + '%';

        if (ticker !== 'TITULARIZADORA') {
          const yieldEl = document.getElementById(`${ticker}-yield`);
          if (yieldEl) yieldEl.textContent = activo.dividendYield + '%';
        } else {
          const tasaEl = document.getElementById(`${ticker}-tasa`);
          if (tasaEl) tasaEl.textContent = activo.tasa + '%';

          const vencEl = document.getElementById(`${ticker}-vencimiento`);
          if (vencEl) vencEl.textContent = activo.vencimiento;
        }
      }
    });

  } catch (error) {
    console.error('Error cargando portafolio:', error);
  }
}

// Cargar transacciones
async function cargarTransacciones() {
  try {
    const response = await fetch('/api/transactions');
    const data = await response.json();
    const container = document.getElementById('transacciones-list');

    if (!data.transactions || data.transactions.length === 0) {
      container.innerHTML = '<p style="color: #64748b;">Sin transacciones registradas</p>';
      return;
    }

    container.innerHTML = data.transactions.map(tx => `
      <div class="transaccion-item">
        <div class="transaccion-header">
          <span>Compra #${tx.id}</span>
          <span>${tx.fecha}</span>
        </div>
        <div class="transaccion-details">
          <p><strong>Activos:</strong> ${tx.activos.map(a => a.ticker || 'Bono').join(', ')}</p>
          <p><strong>Total Neto:</strong> ${formatearMoneda(tx.totalNeto)}</p>
          <p><strong>Comisión:</strong> ${formatearMoneda(tx.comision)}</p>
          ${tx.notas ? `<p><strong>Notas:</strong> ${tx.notas}</p>` : ''}
        </div>
      </div>
    `).join('');

  } catch (error) {
    console.error('Error cargando transacciones:', error);
  }
}

// Abrir modal para actualizar precio
function abrirActualizarPrecio(ticker) {
  document.getElementById('ticker').value = ticker;
  document.getElementById('precioNuevo').value = '';
  document.getElementById('modal-precio').style.display = 'block';
}

// Cerrar modal
function cerrarModal() {
  document.getElementById('modal-precio').style.display = 'none';
}

// Guardar nuevo precio
async function guardarPrecio(event) {
  event.preventDefault();
  const ticker = document.getElementById('ticker').value;
  const precioActual = parseFloat(document.getElementById('precioNuevo').value);

  try {
    const response = await fetch('/api/portfolio/prices', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ ticker, precioActual })
    });

    const result = await response.json();
    if (result.success) {
      cerrarModal();
      cargarPortafolio();
      mostrarExito(`Precio de ${ticker} actualizado a $${formatearMoneda(precioActual)}`);
    } else {
      mostrarError(result.error || 'Error al actualizar precio');
    }
  } catch (error) {
    console.error('Error:', error);
    mostrarError('Error al actualizar precio');
  }
}

// Calcular próxima compra
async function calcularProximaCompra() {
  try {
    const response = await fetch('/api/calculadora');
    const calculo = await response.json();

    const html = `
      <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; border-left: 4px solid #10b981;">
        <h3 style="margin-bottom: 15px; color: #166534;">📋 Próxima Compra Bimestral</h3>

        <div style="margin-bottom: 20px;">
          <h4 style="color: #1e293b; margin-bottom: 10px;">Capital Disponible</h4>
          <p style="font-size: 1.3rem; font-weight: 700; color: #10b981;">${formatearMoneda(calculo.capital)}</p>
        </div>

        <div style="margin-bottom: 20px;">
          <h4 style="color: #1e293b; margin-bottom: 10px;">Distribución</h4>
          <ul style="list-style: none;">
            <li style="margin-bottom: 8px;">
              <span style="font-weight: 600;">GEB:</span> ${calculo.proximaCompra.GEB.cantidad} acciones × $${formatearMoneda(calculo.proximaCompra.GEB.precioUnitario)} = ${formatearMoneda(calculo.proximaCompra.GEB.total)}
            </li>
            <li style="margin-bottom: 8px;">
              <span style="font-weight: 600;">TERPEL:</span> ${calculo.proximaCompra.TERPEL.cantidad} acciones × $${formatearMoneda(calculo.proximaCompra.TERPEL.precioUnitario)} = ${formatearMoneda(calculo.proximaCompra.TERPEL.total)}
            </li>
            <li>
              <span style="font-weight: 600;">TITULARIZADORA:</span> ${formatearMoneda(calculo.proximaCompra.TITULARIZADORA.monto)} @ ${calculo.proximaCompra.TITULARIZADORA.tasa}%
            </li>
          </ul>
        </div>

        <div style="padding-top: 15px; border-top: 2px solid #dcfce7;">
          <p style="margin-bottom: 8px;"><span style="color: #64748b;">Comisión Tríi:</span> -${formatearMoneda(calculo.comision)}</p>
          <p style="font-size: 1.2rem; font-weight: 700; color: #166534;">
            <span>Total Neto: </span>${formatearMoneda(calculo.totalNeto)}
          </p>
        </div>

        <div style="margin-top: 15px;">
          <button class="btn-primary" onclick="registrarCompra()">✅ Registrar Compra</button>
        </div>
      </div>
    `;

    document.getElementById('calculadora-resultado').innerHTML = html;
  } catch (error) {
    console.error('Error:', error);
    mostrarError('Error al calcular');
  }
}

// Registrar compra
async function registrarCompra() {
  try {
    const response = await fetch('/api/calculadora');
    const calculo = await response.json();
    const fecha = new Date().toISOString().split('T')[0];

    const activos = [
      { ticker: 'GEB', cantidad: calculo.proximaCompra.GEB.cantidad, precioUnitario: calculo.proximaCompra.GEB.precioUnitario, total: calculo.proximaCompra.GEB.total },
      { ticker: 'TERPEL', cantidad: calculo.proximaCompra.TERPEL.cantidad, precioUnitario: calculo.proximaCompra.TERPEL.precioUnitario, total: calculo.proximaCompra.TERPEL.total },
      { ticker: 'TITULARIZADORA', monto: calculo.proximaCompra.TITULARIZADORA.monto, tasa: calculo.proximaCompra.TITULARIZADORA.tasa }
    ];

    const transactionResponse = await fetch('/api/transactions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        fecha,
        activos,
        comision: calculo.comision,
        notas: 'Compra bimestral automática'
      })
    });

    const result = await transactionResponse.json();
    if (result.success) {
      cargarTransacciones();
      document.getElementById('calculadora-resultado').innerHTML = '';
      mostrarExito('Compra registrada exitosamente');
    } else {
      mostrarError(result.error || 'Error al registrar compra');
    }
  } catch (error) {
    console.error('Error:', error);
    mostrarError('Error al registrar compra');
  }
}

// Analizar portafolio con Claude AI
async function analizarPortafolio() {
  const btnAnalizar = document.getElementById('btn-analizar');
  const resultadoDiv = document.getElementById('analisis-resultado');

  try {
    btnAnalizar.disabled = true;
    btnAnalizar.textContent = '⏳ Analizando...';
    resultadoDiv.innerHTML = '<p style="color: #64748b;">Esperando análisis de Claude AI...</p>';

    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });

    const result = await response.json();

    if (result.success) {
      resultadoDiv.innerHTML = `
        <div style="color: #1e293b;">
          ${result.analisis.split('\n').map(line =>
            line ? `<p style="margin-bottom: 10px;">${line}</p>` : ''
          ).join('')}
          <p style="margin-top: 20px; font-size: 0.85rem; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 10px;">
            Análisis generado por ${result.modelo}
          </p>
        </div>
      `;
    } else {
      mostrarError(result.error || 'Error al analizar');
    }
  } catch (error) {
    console.error('Error:', error);
    if (error.message.includes('ANTHROPIC_API_KEY')) {
      resultadoDiv.innerHTML = `
        <div style="background: #fef2f2; padding: 15px; border-radius: 8px; border-left: 4px solid #ef4444; color: #7f1d1d;">
          <p><strong>⚠️ API Key no configurada</strong></p>
          <p>Para usar el análisis con Claude AI, necesitas:</p>
          <ol style="margin-left: 20px; margin-top: 10px;">
            <li>Obtener tu API key en <a href="https://console.anthropic.com" target="_blank" style="color: #ef4444;">console.anthropic.com</a></li>
            <li>Crear archivo <code>.env</code> en la raíz del proyecto</li>
            <li>Agregar: <code>ANTHROPIC_API_KEY=tu_api_key_aqui</code></li>
            <li>Reiniciar el servidor</li>
          </ol>
        </div>
      `;
    } else {
      mostrarError('Error al conectar con Claude AI');
    }
  } finally {
    btnAnalizar.disabled = false;
    btnAnalizar.textContent = '🤖 Analizar Portafolio';
  }
}

// GRÁFICOS - Yahoo Finance & TradingView
let chart = null;
let lineSeries = null;
let currentTicker = 'GEB.CL';
let currentPeriod = '5y';
let allHistoricalData = {};
let accionesDisponibles = [];

// Configuración de precios Buffett para cada activo
const buffettPrices = {
  'GEB.CL': { buffett: 2100, justo: 3200 },
  'TERPEL.CL': { buffett: 14000, justo: 20000 },
  'BCOLOMBIA.CL': { buffett: 35000, justo: 50000 },
  'GRUPOSURA.CL': { buffett: 22000, justo: 35000 },
  'ISA.CL': { buffett: 21000, justo: 34000 },
  'ECOPETROL.CL': { buffett: 1800, justo: 3500 },
  'NUTRESA.CL': { buffett: 30000, justo: 50000 },
  'MINEROS.CL': { buffett: 9000, justo: 15000 }
};

// Cargar tabs de acciones dinámicamente
async function cargarTabsAcciones() {
  try {
    const response = await fetch('/api/acciones');
    if (!response.ok) throw new Error('No se pudieron cargar las acciones');

    const result = await response.json();
    accionesDisponibles = result.acciones || [];

    const container = document.getElementById('chart-tabs');
    if (!container) return;

    container.innerHTML = accionesDisponibles.map((accion, idx) => {
      const badgeClass = accion.accion.includes('COMPRA') ? 'badge-compra' :
                        accion.accion.includes('ESPERA') ? 'badge-espera' :
                        'badge-evita';
      const isActive = idx === 0 ? 'active' : '';

      return `
        <button class="tab-btn ${isActive}" onclick="cargarGrafico('${accion.ticker}', this)">
          ${accion.ticker.split('.')[0]}
          <span class="badge ${badgeClass}">${accion.accion.split('(')[0].trim()}</span>
        </button>
      `;
    }).join('');

    // Cargar primer gráfico
    if (accionesDisponibles.length > 0) {
      cargarGrafico(accionesDisponibles[0].ticker);
    }
  } catch (error) {
    console.error('Error cargando tabs de acciones:', error);
    const container = document.getElementById('chart-tabs');
    if (container) {
      container.innerHTML = '<p style="color: #ef4444;">Error al cargar acciones</p>';
    }
  }
}

async function cargarGrafico(ticker, btnElement) {
  try {
    if (!ticker) {
      console.warn('No ticker provided');
      return;
    }

    currentTicker = ticker;

    // Actualizar tab activo
    const tabs = document.querySelectorAll('.tab-btn');
    if (tabs && tabs.length > 0) {
      tabs.forEach(btn => btn.classList.remove('active'));
      if (btnElement) btnElement.classList.add('active');
    }

    // Obtener datos históricos
    const response = await fetch(`/api/historical/${ticker}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();

    if (!result.data || result.data.length === 0) {
      console.warn('No hay datos históricos para ' + ticker);
      return;
    }

    allHistoricalData[ticker] = result.data;
    mostrarGrafico();
    actualizarNivelesPrecio(ticker);
  } catch (error) {
    console.error('Error cargando gráfico:', error);
  }
}

function mostrarGrafico() {
  const container = document.getElementById('chart-container');
  const datos = allHistoricalData[currentTicker];

  if (!datos) return;

  // Filtrar datos por período
  const datosFilados = filtrarPorPeriodo(datos, currentPeriod);

  // Destruir gráfico anterior si existe
  if (chart) {
    chart.remove();
    chart = null;
  }

  // Crear nuevo gráfico
  const chartOptions = {
    layout: {
      textColor: '#1e293b',
      backgroundColor: '#ffffff',
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
      rightOffset: 12,
    },
    crosshair: {
      mode: LightweightCharts.CrosshairMode.Normal,
    },
  };

  chart = LightweightCharts.createChart(container, {
    width: container.clientWidth,
    height: 450,
    ...chartOptions
  });

  // Agregar línea de precios
  lineSeries = chart.addLineSeries({
    color: '#2563eb',
    lineWidth: 2,
  });

  // Preparar datos para el gráfico (convertir a timestamp Unix)
  const dataForChart = datosFilados.map(d => ({
    time: new Date(d.date).getTime() / 1000, // timestamp Unix en segundos
    value: d.close
  }));

  lineSeries.setData(dataForChart);

  // Agregar líneas de referencia (Buffett y precio justo)
  agregarLineasReferencia(datosFilados);

  // Fitear el gráfico al contenedor
  chart.timeScale().fitContent();

  // Agregar volumen como promedio móvil visual
  mostrarEstadisticas(datosFilados);
}

function agregarLineasReferencia(datos) {
  if (!chart) return;

  const config = buffettPrices[currentTicker];
  if (!config) return;

  const timeStart = (new Date(datos[0].date).getTime()) / 1000;
  const timeEnd = (new Date(datos[datos.length - 1].date).getTime()) / 1000;

  // Línea de precio Buffett (verde)
  const buffettSeries = chart.addLineSeries({
    color: '#10b981',
    lineWidth: 1,
    lineStyle: LightweightCharts.LineStyle.Dashed,
    title: 'Precio Buffett'
  });

  buffettSeries.setData([
    { time: timeStart, value: config.buffett },
    { time: timeEnd, value: config.buffett }
  ]);

  // Línea de precio justo (naranja)
  const justoSeries = chart.addLineSeries({
    color: '#f59e0b',
    lineWidth: 1,
    lineStyle: LightweightCharts.LineStyle.Dashed,
    title: 'Precio Justo'
  });

  justoSeries.setData([
    { time: timeStart, value: config.justo },
    { time: timeEnd, value: config.justo }
  ]);
}

function filtrarPorPeriodo(datos, periodo) {
  const now = new Date();
  let fechaLimite;

  switch(periodo) {
    case '1m':
      fechaLimite = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
      break;
    case '3m':
      fechaLimite = new Date(now.getFullYear(), now.getMonth() - 3, now.getDate());
      break;
    case '6m':
      fechaLimite = new Date(now.getFullYear(), now.getMonth() - 6, now.getDate());
      break;
    case '1y':
      fechaLimite = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
      break;
    case '3y':
      fechaLimite = new Date(now.getFullYear() - 3, now.getMonth(), now.getDate());
      break;
    case '5y':
      fechaLimite = new Date(now.getFullYear() - 5, now.getMonth(), now.getDate());
      break;
    default:
      return datos;
  }

  return datos.filter(d => new Date(d.date) >= fechaLimite);
}

function setPeriod(periodo) {
  currentPeriod = periodo;

  // Actualizar botones activos
  document.querySelectorAll('.period-btn').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');

  // Mostrar gráfico con nuevo período
  mostrarGrafico();
}

function mostrarEstadisticas(datos) {
  if (datos.length === 0) return;

  const precios = datos.map(d => d.close);
  const precio_actual = precios[precios.length - 1];
  const precio_min = Math.min(...precios);
  const precio_max = Math.max(...precios);
  const cambio_pct = ((precio_actual - precios[0]) / precios[0] * 100).toFixed(2);

  // Mostrar en los niveles de precio
  const diasEnPeriodo = datos.length;
  const volumenPromedio = (datos.reduce((sum, d) => sum + (d.volume || 0), 0) / diasEnPeriodo).toFixed(0);
}

function actualizarNivelesPrecio(ticker) {
  const config = buffettPrices[ticker];
  if (!config) return;

  document.getElementById('level-buffett').textContent =
    `💚 Precio Buffett: $${formatearMonedaSimple(config.buffett)}`;
  document.getElementById('level-justo').textContent =
    `💛 Precio Justo: $${formatearMonedaSimple(config.justo)}`;

  // Obtener precio actual
  fetch(`/api/price/${ticker}`)
    .then(r => r.json())
    .then(data => {
      document.getElementById('level-actual').textContent =
        `📍 Precio Actual: $${formatearMonedaSimple(data.precioActual)}`;
    })
    .catch(err => console.error('Error obteniendo precio actual:', err));
}

function sincronizarPrecios() {
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = '🔄 Sincronizando...';

  fetch('/api/portfolio/sync-prices', { method: 'PUT' })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        mostrarExito('Precios actualizados desde Yahoo Finance');
        cargarPortafolio();
        cargarGrafico(currentTicker);
      } else {
        mostrarError('Error sincronizando precios');
      }
    })
    .catch(err => {
      console.error('Error:', err);
      mostrarError('Error al sincronizar precios');
    })
    .finally(() => {
      btn.disabled = false;
      btn.textContent = '🔄 Sincronizar Precios desde Yahoo Finance';
    });
}

function formatearMonedaSimple(valor) {
  return valor.toLocaleString('es-CO', { maximumFractionDigits: 0 });
}

// Cargar tabs y gráfico inicial al abrir la página
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    try {
      cargarTabsAcciones();
    } catch (err) {
      console.error('Error cargando tabs:', err);
    }
  }, 500);
});

// Utilidades
function formatearMoneda(valor) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0
  }).format(valor);
}

function mostrarExito(mensaje) {
  alert('✅ ' + mensaje);
}

function mostrarError(mensaje) {
  alert('❌ ' + mensaje);
}

// Cerrar modal al hacer click afuera
window.onclick = function(event) {
  const modal = document.getElementById('modal-precio');
  if (event.target === modal) {
    modal.style.display = 'none';
  }
}
