/**
 * Benjamin Graham Value Investing Analysis Engine
 * Framework completo para análisis fundamental y margen de seguridad
 */

class GrahamAnalyzer {
  constructor() {
    this.ratios = {
      rentabilidad: { weight: 1, max: 5 },
      balance: { weight: 1, max: 5 },
      flujosCaja: { weight: 1.2, max: 5 },
      dividendos: { weight: 1, max: 5 },
      valuacion: { weight: 1.3, max: 5 },
      moat: { weight: 1, max: 5 }
    };
  }

  /**
   * FÓRMULA 1: Graham Number (Valor Intrínseco Simplificado)
   * VI = √(22.5 × EPS × BVPS)
   * 22.5 = P/E × P/B ratio máximo aceptable
   */
  grahamNumber(eps, bvps) {
    if (!eps || !bvps || eps <= 0 || bvps <= 0) return null;
    return Math.sqrt(22.5 * eps * bvps);
  }

  /**
   * FÓRMULA 2: EPV (Earnings Power Value)
   * VI = (EPS × (8.5 + 2g) × 4.4) ÷ r
   * g = tasa crecimiento esperado (%)
   * r = tasa descuento (10% para Graham)
   */
  epv(eps, growthRate = 5, discountRate = 10) {
    if (!eps || eps <= 0) return null;
    const r = discountRate / 100;
    const g = growthRate / 100;
    return (eps * (8.5 + 2 * g) * 4.4) / r;
  }

  /**
   * MARGEN DE SEGURIDAD (El corazón del análisis)
   * MS = (VI - Precio) / VI × 100
   *
   * ≥ 50% = ORO PURO (COMPRA FUERTE)
   * 30-50% = BUENA OPORTUNIDAD (COMPRA)
   * 15-30% = ACEPTABLE (ESPERA/COMPRA PEQUEÑA)
   * < 15% = INSUFICIENTE (ESPERA)
   * < 0% = SOBREVALORADO (EVITA)
   */
  marginSeguridad(valorIntrínseco, precioActual) {
    if (!valorIntrínseco || !precioActual || valorIntrínseco <= 0 || precioActual <= 0) {
      return null;
    }
    return ((valorIntrínseco - precioActual) / valorIntrínseco) * 100;
  }

  /**
   * ANÁLISIS DE RENTABILIDAD (0-5 puntos)
   * Evalúa: EPS growth, ROE, márgenes de ganancia
   */
  analizarRentabilidad(datos) {
    let puntos = 0;

    // ROE (Return on Equity)
    if (datos.roe) {
      if (datos.roe > 20) puntos += 1.5; // Excelente
      else if (datos.roe > 15) puntos += 1; // Bueno
      else if (datos.roe > 10) puntos += 0.5; // Aceptable
    }

    // Crecimiento EPS
    if (datos.epsGrowth) {
      if (datos.epsGrowth > 10) puntos += 1.5; // Excelente
      else if (datos.epsGrowth > 5) puntos += 1; // Bueno
      else if (datos.epsGrowth > 0) puntos += 0.5; // Aceptable
    }

    // Margen neto
    if (datos.netMargin) {
      if (datos.netMargin > 15) puntos += 1; // Excelente
      else if (datos.netMargin > 10) puntos += 0.5; // Bueno
    }

    return Math.min(puntos, 5);
  }

  /**
   * ANÁLISIS DE BALANCE (0-5 puntos)
   * Evalúa: Deuda, liquidez, solvencia
   */
  analizarBalance(datos) {
    let puntos = 0;

    // Razón Deuda/Capital (debe ser < 0.5)
    if (datos.debtToCapital !== undefined) {
      if (datos.debtToCapital < 0.3) puntos += 1.5; // Excelente
      else if (datos.debtToCapital < 0.5) puntos += 1; // Bueno
      else if (datos.debtToCapital < 0.75) puntos += 0.5; // Aceptable
      // Si > 0.75: sin puntos
    }

    // Razón corriente (Activos/Pasivos debe ser > 1.5)
    if (datos.currentRatio !== undefined) {
      if (datos.currentRatio > 2) puntos += 1.5; // Excelente
      else if (datos.currentRatio > 1.5) puntos += 1; // Bueno
      else if (datos.currentRatio > 1) puntos += 0.5; // Aceptable
    }

    // Cash/Deuda total (capacidad de pago)
    if (datos.cashToDebt !== undefined) {
      if (datos.cashToDebt > 0.5) puntos += 1.5; // Excelente
      else if (datos.cashToDebt > 0.25) puntos += 1; // Bueno
      else if (datos.cashToDebt > 0.1) puntos += 0.5; // Aceptable
    }

    return Math.min(puntos, 5);
  }

  /**
   * ANÁLISIS DE FLUJO DE CAJA (0-5 puntos)
   * Evalúa: FCF > 80% ganancias, crecimiento FCF
   */
  analizarFlujoCaja(datos) {
    let puntos = 0;

    // FCF vs Ganancias (debe ser > 80%)
    if (datos.fcfRatio !== undefined) {
      if (datos.fcfRatio > 0.8) puntos += 2; // Excelente
      else if (datos.fcfRatio > 0.6) puntos += 1.5; // Bueno
      else if (datos.fcfRatio > 0.4) puntos += 1; // Aceptable
      else if (datos.fcfRatio > 0) puntos += 0.5; // Débil pero positivo
    }

    // Crecimiento FCF anual
    if (datos.fcfGrowth !== undefined) {
      if (datos.fcfGrowth > 10) puntos += 1.5; // Excelente
      else if (datos.fcfGrowth > 5) puntos += 1; // Bueno
      else if (datos.fcfGrowth > 0) puntos += 0.5; // Aceptable
    }

    return Math.min(puntos, 5);
  }

  /**
   * ANÁLISIS DE DIVIDENDOS (0-5 puntos)
   * Evalúa: Payout ratio 30-70%, crecimiento, sostenibilidad
   */
  analizarDividendos(datos) {
    let puntos = 0;

    // Dividend Yield
    if (datos.dividendYield !== undefined) {
      if (datos.dividendYield > 5) puntos += 1; // Generoso
      else if (datos.dividendYield > 3) puntos += 1.5; // Excelente
      else if (datos.dividendYield > 1) puntos += 1; // Bueno
      else if (datos.dividendYield > 0) puntos += 0.5; // Existe
    }

    // Payout Ratio (30-70% es ideal)
    if (datos.payoutRatio !== undefined) {
      if (datos.payoutRatio > 0.3 && datos.payoutRatio < 0.7) {
        puntos += 1.5; // Óptimo - sostenible
      } else if (datos.payoutRatio > 0.2 && datos.payoutRatio < 0.8) {
        puntos += 1; // Aceptable
      } else if (datos.payoutRatio > 0) {
        puntos += 0.5; // Pero insostenible
      }
    }

    // Crecimiento de dividendos (histórico 5 años)
    if (datos.dividendGrowth !== undefined) {
      if (datos.dividendGrowth > 5) puntos += 1; // Excelente
      else if (datos.dividendGrowth > 0) puntos += 0.5; // Positivo
    }

    return Math.min(puntos, 5);
  }

  /**
   * ANÁLISIS DE VALUACIÓN (0-5 puntos)
   * Evalúa: P/E, PEG, P/B ratios
   */
  analizarValuacion(datos) {
    let puntos = 0;

    // P/E Ratio (ideal < 15)
    if (datos.pe !== undefined) {
      if (datos.pe < 10) puntos += 1.5; // Muy barato
      else if (datos.pe < 15) puntos += 1.5; // Barato
      else if (datos.pe < 20) puntos += 1; // Justo
      else if (datos.pe < 30) puntos += 0.5; // Caro
      // Si > 30: sin puntos
    }

    // PEG Ratio (ideal < 1.5)
    if (datos.peg !== undefined) {
      if (datos.peg < 1) puntos += 1.5; // Muy barato
      else if (datos.peg < 1.5) puntos += 1; // Barato
      else if (datos.peg < 2) puntos += 0.5; // Aceptable
    }

    // P/B Ratio (ideal < 2.0)
    if (datos.pb !== undefined) {
      if (datos.pb < 1) puntos += 1; // Excelente
      else if (datos.pb < 1.5) puntos += 1.5; // Bueno
      else if (datos.pb < 2) puntos += 1; // Aceptable
      else if (datos.pb < 3) puntos += 0.5; // Caro
    }

    return Math.min(puntos, 5);
  }

  /**
   * ANÁLISIS DE MOAT (Foso económico) (0-5 puntos)
   * Evalúa: Ventaja competitiva sostenible
   */
  analizarMoat(datos) {
    let puntos = 0;

    // Basado en descripción del moat
    if (datos.moat) {
      const moatLower = datos.moat.toLowerCase();

      // Mejor: Monopolio/Network effect
      if (
        moatLower.includes('monopolio') ||
        moatLower.includes('network') ||
        moatLower.includes('exclusivo')
      ) {
        puntos = 5;
      }
      // Muy bueno: Marca + Economía de escala
      else if (
        moatLower.includes('marca') ||
        moatLower.includes('marca fuerte') ||
        moatLower.includes('economía de escala')
      ) {
        puntos = 4;
      }
      // Bueno: Costo bajo + Switching cost
      else if (
        moatLower.includes('costo') ||
        moatLower.includes('switching') ||
        moatLower.includes('concesión')
      ) {
        puntos = 3;
      }
      // Débil: Sin ventaja clara
      else if (moatLower.includes('commodity') || moatLower.includes('sin')) {
        puntos = 1;
      } else {
        puntos = 2; // Neutral
      }
    }

    return Math.min(puntos, 5);
  }

  /**
   * ANÁLISIS INTEGRAL GRAHAM (0-30 puntos)
   * Devuelve puntuación total y recomendación
   */
  analisisCompleto(datos) {
    const analisis = {
      rentabilidad: this.analizarRentabilidad(datos),
      balance: this.analizarBalance(datos),
      flujosCaja: this.analizarFlujoCaja(datos),
      dividendos: this.analizarDividendos(datos),
      valuacion: this.analizarValuacion(datos),
      moat: this.analizarMoat(datos)
    };

    const total =
      analisis.rentabilidad +
      analisis.balance +
      analisis.flujosCaja +
      analisis.dividendos +
      analisis.valuacion +
      analisis.moat;

    // Recomendación basada en puntuación
    let recomendacion = 'EVITA';
    if (total >= 20) recomendacion = 'COMPRA';
    else if (total >= 15) recomendacion = 'ESPERA';
    else if (total >= 10) recomendacion = 'EVITA';

    return {
      analisis,
      total,
      recomendacion,
      detalles: {
        '≥ 20': 'COMPRA FUERTE',
        '15-19': 'ESPERA OPORTUNIDAD',
        '10-14': 'EVITA POR AHORA',
        '< 10': 'DEFINITIVAMENTE EVITA'
      }
    };
  }

  /**
   * DECISIÓN FINAL: Combina Puntuación + Margen de Seguridad
   */
  decisionFinal(datos, precioActual) {
    // Calcular valor intrínseco (promedio de dos métodos)
    const vi1 = this.grahamNumber(datos.eps, datos.bvps);
    const vi2 = this.epv(datos.eps, datos.growthRate);
    const valorIntrínseco = vi1 && vi2 ? (vi1 + vi2) / 2 : vi1 || vi2;

    // Calcular margen de seguridad
    const marginSeguridad = this.marginSeguridad(valorIntrínseco, precioActual);

    // Análisis fundamental
    const fundamental = this.analisisCompleto(datos);

    // Decisión combinada
    let acción = 'EVITA';
    let razón = '';
    let confianza = 0;

    if (fundamental.total >= 20 && marginSeguridad >= 30) {
      acción = 'COMPRA FUERTE';
      confianza = Math.min(100, fundamental.total * 3 + marginSeguridad);
    } else if (fundamental.total >= 20 && marginSeguridad >= 15) {
      acción = 'COMPRA';
      confianza = Math.min(100, fundamental.total * 2.5 + marginSeguridad);
    } else if (fundamental.total >= 15 && marginSeguridad >= 30) {
      acción = 'COMPRA PEQUEÑA';
      confianza = Math.min(100, fundamental.total * 2 + marginSeguridad);
    } else if (fundamental.total >= 15 && marginSeguridad >= 15) {
      acción = 'ESPERA';
      razón = 'Fundamental OK pero sin margen suficiente';
      confianza = Math.min(100, fundamental.total + marginSeguridad);
    } else if (marginSeguridad < 0) {
      acción = 'EVITA';
      razón = 'Sobrevalorado - precio por encima de valor intrínseco';
      confianza = 5;
    } else {
      acción = 'EVITA';
      razón = 'Fundamental débil o margen insuficiente';
      confianza = Math.max(0, fundamental.total * 2);
    }

    return {
      acción,
      confianza: Math.round(confianza),
      fundamentalScore: fundamental.total,
      marginSeguridad: marginSeguridad ? Math.round(marginSeguridad * 10) / 10 : null,
      valorIntrínseco: valorIntrínseco ? Math.round(valorIntrínseco * 100) / 100 : null,
      precioActual,
      pozoCompra: valorIntrínseco ? Math.round(valorIntrínseco * 0.67 * 100) / 100 : null,
      razón,
      detalleAnalisis: fundamental
    };
  }
}

module.exports = GrahamAnalyzer;
