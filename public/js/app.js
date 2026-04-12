// Cargar portafolio y gráficos al iniciar
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOMContentLoaded event fired');
  cargarPortafolio();
  cargarTransacciones();

  // Llamar cargarTabsAcciones directamente (no necesita librerías externas con Canvas)
  console.log('Llamando cargarTabsAcciones...');
  cargarTabsAcciones().catch(err => console.error('Error en cargarTabsAcciones:', err));
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
let currentGrahamData = null; // Guardar datos Graham actuales

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
    console.log('Cargando gráfico para:', ticker);

    // Actualizar tab activo
    const tabs = document.querySelectorAll('.tab-btn');
    if (tabs && tabs.length > 0) {
      tabs.forEach(btn => btn.classList.remove('active'));
      if (btnElement) {
        btnElement.classList.add('active');
      } else {
        tabs.forEach(btn => {
          if (btn.textContent.includes(ticker.split('.')[0])) {
            btn.classList.add('active');
          }
        });
      }
    }

    // PASO 1: Obtener datos históricos
    console.log('Fetching historical data for:', ticker);
    const response = await fetch(`/api/historical/${ticker}`);

    if (!response.ok) {
      console.error('Response error:', response.status, response.statusText);
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();
    console.log('Historical data loaded:', result.count, 'records');

    if (!result.data || result.data.length === 0) {
      console.warn('No hay datos históricos para ' + ticker);
      return;
    }

    allHistoricalData[ticker] = result.data;

    // PASO 2: Obtener análisis Graham para valores reales
    console.log('Obteniendo análisis Graham...');
    try {
      const grahamResponse = await fetch(`/api/graham-analysis/${ticker}`);

      if (!grahamResponse.ok) {
        throw new Error(`HTTP ${grahamResponse.status}`);
      }

      const grahamData = await grahamResponse.json();

      if (grahamData.success && grahamData.valorIntrínseco) {
        currentGrahamData = grahamData;
        console.log('✓ Valores Graham obtenidos:', {
          VI: grahamData.valorIntrínseco.promedio,
          confianza: grahamData.valorIntrínseco.confianza,
          accion: grahamData.analisisGraham?.acción
        });
      } else {
        console.warn('Graham data incomplete:', grahamData);
        currentGrahamData = null;
      }
    } catch (e) {
      console.warn('No se pudieron obtener valores Graham:', e.message);
      currentGrahamData = null;
    }

    console.log('Mostrando gráfico...');
    mostrarGrafico();
    actualizarNivelesPrecio(ticker);
  } catch (error) {
    console.error('Error cargando gráfico:', error);
  }
}

function mostrarGrafico() {
  const container = document.getElementById('chart-container');
  const datos = allHistoricalData[currentTicker];

  if (!container) {
    console.error('Chart container not found');
    return;
  }

  if (!datos || datos.length === 0) {
    console.warn('No datos para mostrar gráfico');
    return;
  }

  // Filtrar datos por período
  const datosFilados = filtrarPorPeriodo(datos, currentPeriod);

  // Limpiar container
  container.innerHTML = '';

  try {
    // Crear canvas
    const canvas = document.createElement('canvas');
    canvas.width = container.clientWidth || 800;
    canvas.height = 450;
    canvas.style.display = 'block';
    container.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    const padding = 60;
    const width = canvas.width - padding * 2;
    const height = canvas.height - padding * 2;

    // Obtener min/max de precios INCLUYENDO el precio actual
    const precios = datosFilados.map(d => d.close);
    let minPrice = Math.min(...precios);
    let maxPrice = Math.max(...precios);

    // Asegurar que el rango incluya el precio actual para que no esté fuera de escala
    if (currentGrahamData && currentGrahamData.precioActual) {
      minPrice = Math.min(minPrice, currentGrahamData.precioActual);
      maxPrice = Math.max(maxPrice, currentGrahamData.precioActual);
    }

    // Expandir rango con padding para claridad
    let priceRange = maxPrice - minPrice || 1;
    const padding_percent = 0.1; // 10% de padding
    minPrice = minPrice - (priceRange * padding_percent);
    maxPrice = maxPrice + (priceRange * padding_percent);
    priceRange = maxPrice - minPrice; // Recalcular priceRange después del padding

    // Dibujar fondo
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Dibujar grid
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = padding + (height / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(canvas.width - padding, y);
      ctx.stroke();

      // Labels de precio
      const price = maxPrice - (priceRange / 5) * i;
      ctx.fillStyle = '#64748b';
      ctx.font = '0.8rem sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText('$' + Math.round(price).toLocaleString(), padding - 10, y + 5);
    }

    // Dibujar líneas de referencia usando valores Graham reales
    let precioBuffett = null;
    let precioJusto = null;

    if (currentGrahamData && currentGrahamData.valorIntrínseco) {
      const vi = currentGrahamData.valorIntrínseco.promedio;
      precioBuffett = vi * 0.67; // 67% del VI (Buffett)
      precioJusto = vi;            // 100% del VI (Justo)
    } else {
      // Fallback a valores locales si no hay datos Graham
      const buffettConfig = buffettPrices[currentTicker];
      if (buffettConfig) {
        precioBuffett = buffettConfig.buffett;
        precioJusto = buffettConfig.justo;
      }
    }

    // Línea Buffett (verde) - Entrada ideal
    if (precioBuffett && precioBuffett >= minPrice && precioBuffett <= maxPrice) {
      const y = padding + height - ((precioBuffett - minPrice) / priceRange) * height;
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(canvas.width - padding, y);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 0.75rem sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(`💚 Buffett: $${Math.round(precioBuffett).toLocaleString()}`, padding + 10, y - 5);
    }

    // Línea Precio Justo (naranja)
    if (precioJusto && precioJusto >= minPrice && precioJusto <= maxPrice) {
      const y = padding + height - ((precioJusto - minPrice) / priceRange) * height;
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(canvas.width - padding, y);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 0.75rem sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(`💛 Justo: $${Math.round(precioJusto).toLocaleString()}`, padding + 10, y - 5);
    }

    // Línea Precio Actual (azul sólido)
    if (currentGrahamData && currentGrahamData.precioActual >= minPrice && currentGrahamData.precioActual <= maxPrice) {
      const y = padding + height - ((currentGrahamData.precioActual - minPrice) / priceRange) * height;
      ctx.strokeStyle = '#2563eb';
      ctx.lineWidth = 3;
      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(canvas.width - padding, y);
      ctx.stroke();

      ctx.fillStyle = '#2563eb';
      ctx.font = 'bold 0.75rem sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(`📍 Actual: $${Math.round(currentGrahamData.precioActual).toLocaleString()}`, padding + 10, y + 12);
    }

    // Dibujar línea de precios
    ctx.strokeStyle = '#2563eb';
    ctx.lineWidth = 2;
    ctx.beginPath();

    datosFilados.forEach((d, idx) => {
      const x = padding + (width / (datosFilados.length - 1 || 1)) * idx;
      const y = padding + height - ((d.close - minPrice) / priceRange) * height;

      if (idx === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // Dibujar area bajo la línea
    ctx.fillStyle = 'rgba(37, 99, 235, 0.1)';
    ctx.lineTo(canvas.width - padding, padding + height);
    ctx.lineTo(padding, padding + height);
    ctx.closePath();
    ctx.fill();

    // Dibujar ejes
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, canvas.height - padding);
    ctx.lineTo(canvas.width - padding, canvas.height - padding);
    ctx.stroke();

    // Título
    ctx.fillStyle = '#1e293b';
    ctx.font = 'bold 1.2rem sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`${currentTicker} - Últimos ${datosFilados.length} días`, canvas.width / 2, 30);

    console.log('Gráfico renderizado exitosamente con Canvas');
    mostrarEstadisticas(datosFilados);
  } catch (error) {
    console.error('Error creando gráfico:', error);
    container.innerHTML = '<div style="background: #fef2f2; color: #7f1d1d; padding: 20px; border-radius: 8px; border-left: 4px solid #ef4444;"><p><strong>Error al renderizar gráfico:</strong></p><p>' + error.message + '</p></div>';
  }
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
  // Usar valores Graham reales si están disponibles
  if (currentGrahamData && currentGrahamData.valorIntrínseco) {
    const vi = currentGrahamData.valorIntrínseco.promedio;
    const precioActual = currentGrahamData.precioActual;

    const precioBuffett = vi * 0.67;  // 67% VI
    const precioJusto = vi;            // 100% VI

    document.getElementById('level-buffett').textContent =
      `💚 Precio Buffett: $${formatearMonedaSimple(precioBuffett)} (Graham)`;
    document.getElementById('level-justo').textContent =
      `💛 Precio Justo: $${formatearMonedaSimple(precioJusto)} (Graham)`;
    document.getElementById('level-actual').textContent =
      `📍 Precio Actual: $${formatearMonedaSimple(precioActual)}`;

    console.log('Valores Graham actualizados:', { precioBuffett, precioJusto, precioActual, vi });
  } else {
    // Fallback a valores locales
    const config = buffettPrices[ticker];
    if (!config) return;

    document.getElementById('level-buffett').textContent =
      `💚 Precio Buffett: $${formatearMonedaSimple(config.buffett)}`;
    document.getElementById('level-justo').textContent =
      `💛 Precio Justo: $${formatearMonedaSimple(config.justo)}`;

    fetch(`/api/price/${ticker}`)
      .then(r => r.json())
      .then(data => {
        document.getElementById('level-actual').textContent =
          `📍 Precio Actual: $${formatearMonedaSimple(data.precioActual)}`;
      })
      .catch(err => console.error('Error obteniendo precio actual:', err));
  }
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

// BENJAMIN GRAHAM ANALYSIS
async function analizarGraham() {
  if (!currentTicker) {
    alert('Selecciona una acción primero');
    return;
  }

  const btn = event.target;
  btn.disabled = true;
  btn.textContent = '⏳ Analizando...';

  try {
    const response = await fetch(`/api/graham-analysis/${currentTicker}`);
    const result = await response.json();

    if (result.success && result.analisisGraham) {
      mostrarAnalisisGraham(result);
    } else {
      console.error('Respuesta incompleta:', result);
      alert('Error en análisis: ' + (result.error || 'Datos incompletos'));
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error al conectar con Graham analyzer');
  } finally {
    btn.disabled = false;
    btn.textContent = '📊 Ejecutar Análisis Graham';
  }
}

function mostrarAnalisisGraham(data) {
  const analisis = data.analisisGraham;
  if (!analisis) {
    console.error('No hay analisisGraham en data:', data);
    document.getElementById('graham-resultado').innerHTML = '<p style="color: red;">Error: No se pudo obtener análisis Graham</p>';
    return;
  }

  const { acción, confianza, fundamentalScore, marginSeguridad, valorIntrínseco, precioActual, pozoCompra, detalleAnalisis } = analisis;
  const viCalculado = data.valorIntrínseco?.promedio || valorIntrínseco;

  // Determinar color de acción
  let accionClass = 'evita';
  if (acción.includes('COMPRA')) accionClass = 'compra';
  else if (acción.includes('ESPERA')) accionClass = 'espera';

  const html = `
    <div class="graham-card">
      <div class="graham-header">
        <h3>${data.nombre} (${data.ticker})</h3>
        <div class="graham-accion ${accionClass}">${acción}</div>
      </div>

      <div class="graham-grid">
        <div class="graham-metric">
          <div class="graham-metric-label">Confianza</div>
          <div class="graham-metric-value">${confianza}%</div>
        </div>
        <div class="graham-metric">
          <div class="graham-metric-label">Score Graham</div>
          <div class="graham-metric-value">${fundamentalScore}/30</div>
        </div>
        <div class="graham-metric">
          <div class="graham-metric-label">Margen Seguridad</div>
          <div class="graham-metric-value" style="color: ${marginSeguridad >= 30 ? '#10b981' : '#f59e0b'}">
            ${marginSeguridad}%
          </div>
        </div>
        <div class="graham-metric">
          <div class="graham-metric-label">Precio Actual</div>
          <div class="graham-metric-value" style="color: var(--text)">$${formatearMonedaSimple(precioActual)}</div>
        </div>
      </div>

      <div class="graham-scores">
        <h4 style="margin-top: 0; color: var(--text);">📋 Análisis Fundamental (0-5 puntos cada)</h4>
        <div class="scores-grid">
          <div class="score-item">
            <div class="score-label">Rentabilidad</div>
            <div class="score-bar">
              <div class="score-fill" style="width: ${(detalleAnalisis.analisis.rentabilidad / 5) * 100}%"></div>
            </div>
            <div style="font-size: 0.9rem; font-weight: 600; color: var(--primary);">${detalleAnalisis.analisis.rentabilidad}/5</div>
          </div>
          <div class="score-item">
            <div class="score-label">Balance</div>
            <div class="score-bar">
              <div class="score-fill" style="width: ${(detalleAnalisis.analisis.balance / 5) * 100}%"></div>
            </div>
            <div style="font-size: 0.9rem; font-weight: 600; color: var(--primary);">${detalleAnalisis.analisis.balance}/5</div>
          </div>
          <div class="score-item">
            <div class="score-label">Flujo Caja</div>
            <div class="score-bar">
              <div class="score-fill" style="width: ${(detalleAnalisis.analisis.flujosCaja / 5) * 100}%"></div>
            </div>
            <div style="font-size: 0.9rem; font-weight: 600; color: var(--primary);">${detalleAnalisis.analisis.flujosCaja}/5</div>
          </div>
          <div class="score-item">
            <div class="score-label">Dividendos</div>
            <div class="score-bar">
              <div class="score-fill" style="width: ${(detalleAnalisis.analisis.dividendos / 5) * 100}%"></div>
            </div>
            <div style="font-size: 0.9rem; font-weight: 600; color: var(--primary);">${detalleAnalisis.analisis.dividendos}/5</div>
          </div>
          <div class="score-item">
            <div class="score-label">Valuación</div>
            <div class="score-bar">
              <div class="score-fill" style="width: ${(detalleAnalisis.analisis.valuacion / 5) * 100}%"></div>
            </div>
            <div style="font-size: 0.9rem; font-weight: 600; color: var(--primary);">${detalleAnalisis.analisis.valuacion}/5</div>
          </div>
          <div class="score-item">
            <div class="score-label">Moat</div>
            <div class="score-bar">
              <div class="score-fill" style="width: ${(detalleAnalisis.analisis.moat / 5) * 100}%"></div>
            </div>
            <div style="font-size: 0.9rem; font-weight: 600; color: var(--primary);">${detalleAnalisis.analisis.moat}/5</div>
          </div>
        </div>
      </div>

      <div class="graham-grid">
        <div class="graham-metric" style="border-left-color: #10b981;">
          <div class="graham-metric-label">💚 Precio Buffett (Entrada ideal)</div>
          <div class="graham-metric-value" style="color: #10b981;">$${formatearMonedaSimple(viCalculado * 0.67)}</div>
        </div>
        <div class="graham-metric" style="border-left-color: #f59e0b;">
          <div class="graham-metric-label">💛 Precio Justo (VI)</div>
          <div class="graham-metric-value" style="color: #f59e0b;">$${formatearMonedaSimple(viCalculado)}</div>
        </div>
        <div class="graham-metric" style="border-left-color: #ef4444;">
          <div class="graham-metric-label">🔥 Pozo de Compra (Máximo -33%)</div>
          <div class="graham-metric-value" style="color: #ef4444;">$${formatearMonedaSimple(viCalculado * 0.67)}</div>
        </div>
      </div>

      ${data.moat ? `
        <div style="background: #f0fdf4; padding: 15px; border-radius: 8px; margin-top: 15px; border-left: 4px solid var(--success);">
          <strong style="color: var(--success);">🏰 Moat (Foso Económico):</strong>
          <p style="margin: 8px 0 0 0; color: var(--text);">${data.moat}</p>
        </div>
      ` : ''}

      ${analisis.razón ? `<div class="graham-razon">⚠️ ${analisis.razón}</div>` : ''}

      <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; margin-top: 15px; border-left: 4px solid var(--primary);">
        <strong style="color: var(--primary);">📊 Interpretación:</strong>
        <ul style="margin: 10px 0 0 20px; color: var(--text);">
          <li><strong>≥ 20 puntos:</strong> COMPRA - Fundamental sólido</li>
          <li><strong>15-19 puntos:</strong> ESPERA - Espera mejor precio</li>
          <li><strong>&lt; 15 puntos:</strong> EVITA - No cumple criterios</li>
          <li><strong>Margen ≥ 30%:</strong> Margen de seguridad adecuado</li>
          <li><strong>Margen &lt; 15%:</strong> Sin margen de seguridad</li>
        </ul>
      </div>
    </div>
  `;

  document.getElementById('graham-resultado').innerHTML = html;
}

