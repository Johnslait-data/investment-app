#!/usr/bin/env node

const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const Anthropic = require('@anthropic-ai/sdk');

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

// Función para generar datos históricos realistas para testing
// (En producción, se conectaría a Yahoo Finance real)
function generateHistoricalData(ticker) {
  const data = [];
  const startDate = new Date(2021, 0, 1);
  const endDate = new Date();
  const dayMs = 24 * 60 * 60 * 1000;

  let basePrice = BASE_PRICES[ticker] || BASE_PRICES['GEB.CL'];
  let currentPrice = basePrice;

  for (let d = new Date(startDate); d <= endDate; d.setTime(d.getTime() + dayMs)) {
    // Simular volatilidad realista (±2% diarios)
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

// Función para obtener precio actual (simulado pero realista)
function getCurrentPrice(ticker) {
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

// GET /api/price/:ticker - Obtener precio actual (simulado para demo)
app.get('/api/price/:ticker', (req, res) => {
  try {
    const ticker = req.params.ticker;
    const precioActual = getCurrentPrice(ticker);

    if (!precioActual) {
      return res.status(404).json({ error: `Ticker ${ticker} no encontrado` });
    }

    // Simular cambios pequeños aleatorios
    const cambioProcentaje = (Math.random() - 0.5) * 0.02; // ±1%
    const cambio = precioActual * cambioProcentaje;

    res.json({
      ticker,
      precioActual: Math.round(precioActual * 100) / 100,
      precioApertura: Math.round((precioActual - cambio) * 100) / 100,
      precioAlto: Math.round(precioActual * 1.005 * 100) / 100,
      precioBajo: Math.round(precioActual * 0.995 * 100) / 100,
      volumen: Math.floor(Math.random() * 5000000) + 1000000,
      cambio: Math.round(cambio * 100) / 100,
      cambioProcentaje: Math.round(cambioProcentaje * 10000) / 100,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: `Error obteniendo precio: ${error.message}` });
  }
});

// GET /api/historical/:ticker - Obtener datos históricos (5 años con cache)
app.get('/api/historical/:ticker', (req, res) => {
  try {
    const ticker = req.params.ticker;

    // Validar que ticker sea válido
    if (!BASE_PRICES[ticker]) {
      return res.status(404).json({ error: `Ticker ${ticker} no soportado` });
    }

    // Intentar cargar del cache
    let data = loadCache(ticker);

    if (!data) {
      // Si no hay cache, generar datos realistas
      data = generateHistoricalData(ticker);
      // Guardar en cache
      saveCache(ticker, data);
    }

    res.json({
      ticker,
      count: data.length,
      data: data,
      source: 'Datos simulados (Demo) - En producción usaría Yahoo Finance'
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

// PUT /api/portfolio/sync-prices - Sincronizar precios (simulado para demo)
app.put('/api/portfolio/sync-prices', (req, res) => {
  try {
    const portfolio = loadPortfolio();

    // Simular pequeñas variaciones aleatorias en precios
    portfolio.activos.GEB.precioActual = Math.round(getCurrentPrice('GEB.CL') * (1 + (Math.random() - 0.5) * 0.02) * 100) / 100;
    portfolio.activos.TERPEL.precioActual = Math.round(getCurrentPrice('TERPEL.CL') * (1 + (Math.random() - 0.5) * 0.02) * 100) / 100;

    savePortfolio(portfolio);

    res.json({
      success: true,
      actualizado: true,
      portfolio: portfolio.activos,
      timestamp: new Date().toISOString(),
      nota: 'Precios sincronizados (Demo con datos simulados - En producción usaría Yahoo Finance)'
    });
  } catch (error) {
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
