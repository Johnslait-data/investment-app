/**
 * Data Fetcher - Obtiene datos fundamentales de Yahoo Finance
 * Combina múltiples fuentes para análisis completo
 */

const axios = require('axios');

class DatosFetcher {
  /**
   * Obtener datos fundamentales de Yahoo Finance
   * Intenta obtener: EPS, P/E, ROE, Deuda, Cash Flow, etc.
   */
  static async obtenerDatosYahoo(ticker) {
    try {
      const headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      };

      // Query a Yahoo Finance API para datos fundamentales
      const response = await axios.get(
        `https://query1.finance.yahoo.com/v10/finance/quoteSummary/${ticker}?modules=defaultKeyStatistics,financialData,quoteType`,
        { headers, timeout: 8000 }
      );

      const result = response.data?.quoteSummary?.result?.[0];
      if (!result) return null;

      const keyStats = result.defaultKeyStatistics || {};
      const finData = result.financialData || {};

      return {
        pe: keyStats.trailingPE?.raw || null,
        forwardPe: keyStats.forwardPE?.raw || null,
        pb: keyStats.priceToBook?.raw || null,
        roe: keyStats.returnOnEquity?.raw || null,
        debtToEquity: keyStats.debtToEquity?.raw || null,
        currentRatio: keyStats.currentRatio?.raw || null,
        quickRatio: keyStats.quickRatio?.raw || null,
        enterpriseValue: keyStats.enterpriseValue?.raw || null,
        marketCap: keyStats.marketCap?.raw || null,
        eps: keyStats.trailingEps?.raw || null,
        revenuePerShare: keyStats.revenuePerShare?.raw || null,
        operatingCashflow: finData.operatingCashflow?.raw || null,
        freeCashflow: finData.freeCashflow?.raw || null,
        totalDebt: finData.totalDebt?.raw || null,
        totalCash: finData.totalCash?.raw || null,
        operatingMargins: finData.operatingMargins?.raw || null,
        netMargins: finData.netMargins?.raw || null,
        profitMargins: finData.profitMargins?.raw || null,
        returnOnAssets: finData.returnOnAssets?.raw || null
      };
    } catch (error) {
      console.warn(`Error fetching Yahoo data for ${ticker}:`, error.message);
      return null;
    }
  }

  /**
   * Calcular métricas derivadas
   */
  static calcularMetricas(precioActual, datos) {
    const metricas = { ...datos };

    // Si no tenemos P/E pero tenemos EPS
    if (!metricas.pe && metricas.eps && metricas.eps > 0) {
      metricas.pe = precioActual / metricas.eps;
    }

    // PEG: P/E / Crecimiento (asumimos 5-7% si no tenemos)
    if (metricas.pe && metricas.pe > 0) {
      const growthRate = 5; // Tasa de crecimiento conservadora
      metricas.peg = metricas.pe / growthRate;
    }

    // PB: si no tenemos, estimar de P/E y ROE
    if (!metricas.pb && metricas.pe && metricas.roe) {
      metricas.pb = metricas.pe / (metricas.roe * 100);
    }

    // FCF Ratio: Free Cash Flow / Net Income
    if (metricas.freeCashflow && metricas.operatingCashflow) {
      metricas.fcfRatio = metricas.freeCashflow / (metricas.operatingCashflow || 1);
    }

    // Debt to Capital
    if (metricas.totalDebt && metricas.marketCap) {
      metricas.debtToCapital = metricas.totalDebt / (metricas.totalDebt + metricas.marketCap);
    }

    // Cash to Debt
    if (metricas.totalCash && metricas.totalDebt && metricas.totalDebt > 0) {
      metricas.cashToDebt = metricas.totalCash / metricas.totalDebt;
    }

    return metricas;
  }

  /**
   * Calcular Valor Intrínseco usando múltiples métodos
   */
  static calcularValorIntrínseco(precioActual, datos, dividendYield = 0) {
    const métodos = {};

    // MÉTODO 1: Graham Number (si tenemos EPS)
    if (datos.eps && datos.pb) {
      try {
        const bvps = precioActual / datos.pb;
        if (datos.eps > 0 && bvps > 0) {
          métodos.graham = Math.sqrt(22.5 * datos.eps * bvps);
        }
      } catch (e) {
        console.warn('Error calculating Graham Number');
      }
    }

    // MÉTODO 2: P/E múltiple (comparar con histórico)
    if (datos.pe && datos.pe > 0) {
      // Precio justo = EPS × P/E promedio histórico (15 es conservador)
      const eps = precioActual / datos.pe;
      métodos.pe = eps * 15; // P/E histórico promedio
    }

    // MÉTODO 3: Dividendo (DCF simplificado)
    if (dividendYield > 0) {
      const dividendoAnual = precioActual * dividendYield;
      // Valor = Dividendo / Tasa de descuento
      const tasaDescuento = 0.10; // 10% tasa de descuento conservadora
      métodos.dividendo = dividendoAnual / tasaDescuento;
    }

    // MÉTODO 4: Book Value (P/B múltiple)
    if (datos.pb && datos.pb > 0) {
      const bookValue = precioActual / datos.pb;
      // Valor justo = Book Value × P/B promedio (2.0 es conservador)
      métodos.pb = bookValue * 2.0;
    }

    // MÉTODO 5: DCF basado en flujo libre de caja
    if (datos.freeCashflow && datos.marketCap) {
      try {
        const fcfPerShare = datos.freeCashflow / (datos.marketCap / precioActual);
        if (fcfPerShare > 0) {
          // DCF simplificado: FCF / Tasa descuento
          métodos.fcf = (fcfPerShare * 1.05) / 0.10; // 5% crecimiento, 10% descuento
        }
      } catch (e) {
        console.warn('Error calculating FCF value');
      }
    }

    // PROMEDIO de todos los métodos disponibles
    const valores = Object.values(métodos).filter((v) => v && v > 0 && isFinite(v));

    if (valores.length === 0) {
      return null;
    }

    const promedio = valores.reduce((a, b) => a + b, 0) / valores.length;

    return {
      promedio: Math.round(promedio * 100) / 100,
      métodos,
      confianza: Math.min(100, valores.length * 25) // 25% por cada método disponible
    };
  }
}

module.exports = DatosFetcher;
