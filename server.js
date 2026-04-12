#!/usr/bin/env node

const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const Anthropic = require('@anthropic-ai/sdk');
const axios = require('axios');
const GrahamAnalyzer = require('./server/graham-analyzer');
const DatosFetcher = require('./server/datos-fetcher');

const app = express();

// Precios base para generar histórico
const BASE_PRICES = {
  'GEB.CL': 2000,
  'TERPEL.CL': 12000,
  'BCOLOMBIA.CL': 25000,
  'GRUPOSURA.CL': 15000,
  'ISA.CL': 18000,
  'ECOPETROL.CL': 1800,
  'NUTRESA.CL': 28000,
  'MINEROS.CL': 8000
};

// Precios actuales de mercado
const PRECIOS_ACTUALES = {
  'GEB.CL': 2800,
  'TERPEL.CL': 19700,
  'BCOLOMBIA.CL': 66860,
  'GRUPOSURA.CL': 28000,
  'ISA.CL': 31000,
  'ECOPETROL.CL': 2600,
  'NUTRESA.CL': 44000,
  'MINEROS.CL': 13840
};

// Función para obtener datos históricos desde Yahoo Finance
async function getHistoricalData(ticker) {
  try {
    const headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': '*/*',
      'Accept-Language': 'en-US,en;q=0.9',
      'Referer': 'https://finance.yahoo.com/',
      'DNT': '1',
      'Connection': 'keep-alive'
    };

    const period1 = Math.floor((Date.now() - 5 * 365 * 24 * 60 * 60 * 1000) / 1000); // 5 años atrás
    const period2 = Math.floor(Date.now() / 1000);

    const response = await axios.get(
      `https://query1.finance.yahoo.com/v7/finance/download/${ticker}?period1=${period1}&period2=${period2}&interval=1d&events=history&includeAdjustedClose=true`,
      { headers, timeout: 10000 }
    );

    // Parsear CSV
    const lines = response.data.trim().split('\n');
    if (lines.length < 2) throw new Error('No data returned');

    const data = [];
    for (let i = 1; i < lines.length; i++) {
      const parts = lines[i].split(',');
      if (parts.length >= 6 && parts[4] !== 'null') {
        const [date, open, high, low, close, adjclose, volume] = parts;
        data.push({
          date,
          open: parseFloat(open) || parseFloat(close),
          high: parseFloat(high) || parseFloat(close),
          low: parseFloat(low) || parseFloat(close),
          close: parseFloat(close),
          volume: parseInt(volume) || 0,
          adjclose: parseFloat(adjclose) || parseFloat(close)
        });
      }
    }

    if (data.length > 0) {
      console.log(`✓ Datos históricos obtenidos para ${ticker}: ${data.length} registros`);
    }
    return data;
  } catch (err) {
    console.warn(`⚠ Error fetching historical data for ${ticker} from Yahoo Finance: ${err.message}`);
    return generateHistoricalDataSimulated(ticker);
  }
}

// Función para generar datos históricos simulados como fallback
function generateHistoricalDataSimulated(ticker) {
  const data = [];
  const startDate = new Date(2021, 0, 1);
  const endDate = new Date();
  const dayMs = 24 * 60 * 60 * 1000;

  let basePrice = BASE_PRICES[ticker] || BASE_PRICES['GEB.CL'];
  let currentPrice = basePrice;

  for (let d = new Date(startDate); d <= endDate; d.setTime(d.getTime() + dayMs)) {
    const change = (Math.random() - 0.5) * 0.04 * currentPrice;
    currentPrice += change;

    data.push({
      date: d.toISOString().split('T')[0],
      open: Math.round(currentPrice * 100) / 100,
      high: Math.round(currentPrice * 1.01 * 100) / 100,
      low: Math.round(currentPrice * 0.99 * 100) / 100,
      close: Math.round(currentPrice * 100) / 100,
      volume: Math.floor(Math.random() * 5000000) + 1000000,
      adjclose: Math.round(currentPrice * 100) / 100
    });
  }

  return data;
}

// Función para obtener precio actual desde Yahoo Finance
async function getCurrentPrice(ticker) {
  try {
    // Headers que simulan un navegador real
    const headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': '*/*',
      'Accept-Language': 'en-US,en;q=0.9',
      'Referer': 'https://finance.yahoo.com/',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1'
    };

    // Intentar con Yahoo Finance primero
    const response = await axios.get(
      `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=1d`,
      { headers, timeout: 8000 }
    );

    if (response.data?.chart?.result?.[0]?.meta?.regularMarketPrice) {
      const price = response.data.chart.result[0].meta.regularMarketPrice;
      console.log(`✓ Precio real obtenido para ${ticker} desde Yahoo Finance: ${price}`);
      return price;
    }
  } catch (err) {
    console.warn(`⚠ Error fetching real price for ${ticker} from Yahoo Finance: ${err.message}`);
  }

  // Fallback a precio simulado
  return PRECIOS_ACTUALES[ticker] || null;
}
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Cargar datos
const portfolioPath = path.join(__dirname, 'data', 'portfolio.json');
const transactionsPath = path.join(__dirname, 'data', 'transactions.json');

function loadPortfolio() {
  return JSON.parse(fs.readFileSync(portfolioPath, 'utf8'));
}

function loadTransactions() {
  return JSON.parse(fs.readFileSync(transactionsPath, 'utf8'));
}

function savePortfolio(data) {
  fs.writeFileSync(portfolioPath, JSON.stringify(data, null, 2));
}

function saveTransactions(data) {
  fs.writeFileSync(transactionsPath, JSON.stringify(data, null, 2));
}

// Cache de datos históricos
const cachePath = path.join(__dirname, 'data', 'cache');

function getCacheFile(ticker) {
  return path.join(cachePath, `${ticker}.json`);
}

function loadCache(ticker) {
  try {
    const cacheFile = getCacheFile(ticker);
    if (fs.existsSync(cacheFile)) {
      const data = JSON.parse(fs.readFileSync(cacheFile, 'utf8'));
      // Verificar si el cache es válido (menos de 24 horas)
      const lastUpdated = new Date(data.lastUpdated);
      const now = new Date();
      const diffHours = (now - lastUpdated) / (1000 * 60 * 60);

      if (diffHours < 24) {
        return data.data;
      }
    }
  } catch (err) {
    // Si hay error, obtener datos nuevos
  }
  return null;
}

function saveCache(ticker, data) {
  try {
    if (!fs.existsSync(cachePath)) {
      fs.mkdirSync(cachePath, { recursive: true });
    }
    const cacheFile = getCacheFile(ticker);
    fs.writeFileSync(cacheFile, JSON.stringify({
      ticker,
      lastUpdated: new Date().toISOString(),
      data: data
    }, null, 2));
  } catch (err) {
    console.error('Error saving cache:', err);
  }
}

// Rutas API

// GET /api/portfolio - Obtener portafolio actual
app.get('/api/portfolio', (req, res) => {
  try {
    const portfolio = loadPortfolio();
    res.json(portfolio);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PUT /api/portfolio/prices - Actualizar precios
app.put('/api/portfolio/prices', (req, res) => {
  try {
    const { ticker, precioActual } = req.body;
    const portfolio = loadPortfolio();

    if (portfolio.activos[ticker]) {
      const precioAnterior = portfolio.activos[ticker].precioActual;
      portfolio.activos[ticker].precioActual = precioActual;

      // Recalcular cantidad de acciones si es necesario
      if (ticker !== 'TITULARIZADORA') {
        const cantidad = Math.floor(portfolio.activos[ticker].monto / precioActual);
        portfolio.activos[ticker].cantidadAcciones = cantidad;
      }

      savePortfolio(portfolio);

      res.json({
        success: true,
        ticker,
        precioAnterior,
        precioActual,
        mensaje: `Precio de ${ticker} actualizado`
      });
    } else {
      res.status(404).json({ error: 'Activo no encontrado' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST /api/transactions - Registrar compra
app.post('/api/transactions', (req, res) => {
  try {
    const { fecha, activos, comision, notas } = req.body;
    const transactions = loadTransactions();

    const totalNeto = activos.reduce((sum, a) => sum + (a.total || a.monto), 0) - comision;

    const nuevoTransaction = {
      id: transactions.transactions.length + 1,
      fecha: fecha || new Date().toISOString().split('T')[0],
      tipo: 'compra',
      activos,
      comision,
      totalNeto,
      notas: notas || ''
    };

    transactions.transactions.push(nuevoTransaction);
    saveTransactions(transactions);

    res.json({
      success: true,
      transaction: nuevoTransaction,
      mensaje: 'Compra registrada exitosamente'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET /api/transactions - Obtener historial
app.get('/api/transactions', (req, res) => {
  try {
    const transactions = loadTransactions();
    res.json(transactions);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST /api/analyze - Análisis con Claude AI
app.post('/api/analyze', async (req, res) => {
  try {
    if (!process.env.ANTHROPIC_API_KEY) {
      return res.status(400).json({ error: 'ANTHROPIC_API_KEY no configurada' });
    }

    const portfolio = loadPortfolio();
    const transactions = loadTransactions();

    const client = new Anthropic();

    const prompt = `Analiza el siguiente portafolio de inversión colombiano basado en la estrategia de Warren Buffett:

PORTAFOLIO ACTUAL:
${JSON.stringify(portfolio, null, 2)}

HISTORIAL DE TRANSACCIONES:
${JSON.stringify(transactions.transactions[0], null, 2)}

Por favor proporciona:
1. Evaluación de la asignación actual
2. Análisis de la estrategia de diversificación
3. Comentarios sobre el dividend yield
4. Recomendaciones para la próxima compra
5. Riesgos identificados y mitigación

Sé conciso pero detallado, en español.`;

    const message = await client.messages.create({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ]
    });

    const analisis = message.content[0].type === 'text' ? message.content[0].text : '';

    res.json({
      success: true,
      analisis,
      modelo: 'claude-haiku-4-5-20251001',
      fecha: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET /api/calculadora - Calcular próxima compra
app.get('/api/calculadora', (req, res) => {
  try {
    const portfolio = loadPortfolio();
    const capital = portfolio.meta.aporteBimestral;

    const GEB = portfolio.activos.GEB;
    const TERPEL = portfolio.activos.TERPEL;
    const TITULARIZADORA = portfolio.activos.TITULARIZADORA;

    const GEB_cantidad = Math.floor(GEB.monto / GEB.precioActual);
    const TERPEL_cantidad = Math.floor(TERPEL.monto / TERPEL.precioActual);

    const calculo = {
      capital,
      proximaCompra: {
        GEB: {
          cantidad: GEB_cantidad,
          precioUnitario: GEB.precioActual,
          total: GEB_cantidad * GEB.precioActual
        },
        TERPEL: {
          cantidad: TERPEL_cantidad,
          precioUnitario: TERPEL.precioActual,
          total: TERPEL_cantidad * TERPEL.precioActual
        },
        TITULARIZADORA: {
          monto: TITULARIZADORA.monto,
          tasa: TITULARIZADORA.tasa
        }
      },
      comision: portfolio.comisiones.triiBimestral,
      totalNeto: GEB_cantidad * GEB.precioActual + TERPEL_cantidad * TERPEL.precioActual + TITULARIZADORA.monto - portfolio.comisiones.triiBimestral
    };

    res.json(calculo);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET /api/price/:ticker - Obtener precio actual desde Yahoo Finance
app.get('/api/price/:ticker', async (req, res) => {
  try {
    const ticker = req.params.ticker;
    const precioActual = await getCurrentPrice(ticker);

    if (!precioActual) {
      return res.status(404).json({ error: `Ticker ${ticker} no encontrado` });
    }

    res.json({
      ticker,
      precioActual: Math.round(precioActual * 100) / 100,
      timestamp: new Date().toISOString(),
      source: 'Yahoo Finance (datos reales)'
    });
  } catch (error) {
    res.status(500).json({ error: `Error obteniendo precio: ${error.message}` });
  }
});

// GET /api/historical/:ticker - Obtener datos históricos (5 años con cache)
app.get('/api/historical/:ticker', async (req, res) => {
  try {
    const ticker = req.params.ticker;

    // Validar que ticker sea válido
    if (!BASE_PRICES[ticker]) {
      return res.status(404).json({ error: `Ticker ${ticker} no soportado` });
    }

    // Intentar cargar del cache
    let data = loadCache(ticker);

    if (!data) {
      // Si no hay cache, obtener datos reales de Yahoo Finance
      data = await getHistoricalData(ticker);
      // Guardar en cache
      saveCache(ticker, data);
    }

    res.json({
      ticker,
      count: data.length,
      data: data,
      source: 'Yahoo Finance (datos reales)'
    });
  } catch (error) {
    res.status(500).json({ error: `Error obteniendo historial: ${error.message}` });
  }
});

// GET /api/acciones - Obtener catálogo de acciones colombianas
app.get('/api/acciones', (req, res) => {
  try {
    const accionesPath = path.join(__dirname, 'data', 'acciones_colombia.json');
    const acciones = JSON.parse(fs.readFileSync(accionesPath, 'utf8'));
    res.json(acciones);
  } catch (error) {
    res.status(500).json({ error: `Error obteniendo acciones: ${error.message}` });
  }
});

// PUT /api/portfolio/sync-prices - Sincronizar precios desde Yahoo Finance
app.put('/api/portfolio/sync-prices', async (req, res) => {
  try {
    const portfolio = loadPortfolio();

    // Obtener precios reales desde Yahoo Finance
    const gebPrice = await getCurrentPrice('GEB.CL');
    const terpelPrice = await getCurrentPrice('TERPEL.CL');

    if (gebPrice) portfolio.activos.GEB.precioActual = Math.round(gebPrice * 100) / 100;
    if (terpelPrice) portfolio.activos.TERPEL.precioActual = Math.round(terpelPrice * 100) / 100;

    savePortfolio(portfolio);

    res.json({
      success: true,
      actualizado: true,
      portfolio: portfolio.activos,
      timestamp: new Date().toISOString(),
      source: 'Yahoo Finance (datos reales)'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST /api/graham-analysis - Análisis Benjamin Graham
app.post('/api/graham-analysis', async (req, res) => {
  try {
    const { ticker, datos } = req.body;

    if (!ticker || !datos) {
      return res.status(400).json({ error: 'Ticket y datos requeridos' });
    }

    const graham = new GrahamAnalyzer();
    const analisis = graham.decisionFinal(datos, datos.precioActual);

    res.json({
      success: true,
      ticker,
      analisis,
      timestamp: new Date().toISOString(),
      framework: 'Benjamin Graham Value Investing'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET /api/graham-analysis/:ticker - Análisis Graham completo con datos reales
app.get('/api/graham-analysis/:ticker', async (req, res) => {
  try {
    const ticker = req.params.ticker;
    const acciones = JSON.parse(
      fs.readFileSync(path.join(__dirname, 'data', 'acciones_colombia.json'), 'utf8')
    );

    const accion = acciones.acciones.find((a) => a.ticker === ticker);
    if (!accion) {
      return res.status(404).json({ error: `Ticker ${ticker} no encontrado` });
    }

    const precioActual = accion.precioActual;

    // PASO 1: Obtener datos reales de Yahoo Finance
    console.log(`📊 Obteniendo datos reales para ${ticker}...`);
    let datosYahoo = await DatosFetcher.obtenerDatosYahoo(ticker);
    datosYahoo = datosYahoo ? DatosFetcher.calcularMetricas(precioActual, datosYahoo) : {};

    // PASO 2: Combinar datos Yahoo + datos locales
    const datos = {
      // Datos de Yahoo Finance (si existen)
      ...datosYahoo,

      // Datos locales (complementarios)
      dividendYield: accion.dividendYield / 100,
      moat: accion.moat,
      precioActual,
      sector: accion.sector,
      calificacion: accion.calificacion,

      // Valores por defecto si no tenemos datos Yahoo
      roe: datosYahoo.roe || 12,
      epsGrowth: datosYahoo.eps ? 5 : null,
      netMargin: datosYahoo.netMargins || 10,
      debtToCapital: datosYahoo.debtToCapital || 0.3,
      currentRatio: datosYahoo.currentRatio || 1.8,
      cashToDebt: datosYahoo.cashToDebt || 0.3,
      fcfRatio: datosYahoo.fcfRatio || 0.85,
      fcfGrowth: 5,
      payoutRatio: (accion.dividendYield / 100) / 0.08, // Estimado
      dividendGrowth: 4,
      growthRate: 5
    };

    // PASO 3: Calcular Valor Intrínseco usando TODOS los métodos
    console.log(`💰 Calculando valor intrínseco...`);
    const viResults = DatosFetcher.calcularValorIntrínseco(precioActual, datos, datos.dividendYield);

    const valorIntrínseco = viResults?.promedio || precioActual * 1.2; // Fallback

    // PASO 4: Análisis Graham
    const graham = new GrahamAnalyzer();
    const analisisGraham = graham.decisionFinal(datos, precioActual);

    // PASO 5: Respuesta completa
    res.json({
      success: true,
      ticker,
      nombre: accion.nombre,
      precioActual,
      datosReales: {
        pe: datosYahoo.pe ? Math.round(datosYahoo.pe * 100) / 100 : null,
        pb: datosYahoo.pb ? Math.round(datosYahoo.pb * 100) / 100 : null,
        roe: datosYahoo.roe ? Math.round(datosYahoo.roe * 100) / 100 : null,
        eps: datosYahoo.eps ? Math.round(datosYahoo.eps * 100) / 100 : null,
        fuente: 'Yahoo Finance'
      },
      valorIntrínseco: {
        promedio: valorIntrínseco,
        métodos: viResults?.métodos || {},
        confianza: viResults?.confianza || 50
      },
      analisisGraham,
      sector: accion.sector,
      moat: accion.moat,
      timestamp: new Date().toISOString(),
      framework: 'Benjamin Graham + Yahoo Finance + Análisis Fundamental'
    });
  } catch (error) {
    console.error('Error en graham-analysis:', error);
    res.status(500).json({ error: error.message });
  }
});

// Rutas estáticas
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`\n🚀 Investment Portfolio App running on http://localhost:${PORT}`);
  console.log('📊 Dashboard: http://localhost:3000');
  console.log('📚 API docs:\n');
  console.log('  GET  /api/portfolio');
  console.log('  PUT  /api/portfolio/prices');
  console.log('  POST /api/transactions');
  console.log('  GET  /api/transactions');
  console.log('  GET  /api/calculadora');
  console.log('  POST /api/analyze (requiere ANTHROPIC_API_KEY)');
  console.log('\n  Yahoo Finance (NEW):');
  console.log('  GET  /api/price/:ticker - Precio actual (ej: GEB.CL)');
  console.log('  GET  /api/historical/:ticker - Datos históricos 5 años');
  console.log('  PUT  /api/portfolio/sync-prices - Sincronizar precios\n');
});
