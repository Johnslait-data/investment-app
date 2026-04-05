# 📊 Investment Portfolio App - Colombia 2026

**Warren Buffett Value Investing Strategy for John**

Una aplicación web local completa para gestionar tu portafolio de inversiones colombianas con análisis de inteligencia artificial.

---

## 🚀 Quick Start

### 1. Instalar dependencias
```bash
npm install
```

### 2. Configurar Claude AI (Opcional)
```bash
# Crea archivo .env
echo "ANTHROPIC_API_KEY=tu_api_key_aqui" > .env
```

### 3. Iniciar servidor
```bash
npm start
# O: node server.js
```

### 4. Abrir en navegador
```
http://localhost:3000
```

---

## 📁 Estructura del Proyecto

```
investment-app/
├── 📄 server.js                 # Express backend + API
├── 📄 package.json              # Dependencias npm
├── 📄 .env.example              # Template para API key
│
├── 📁 data/
│   ├── portfolio.json           # Datos del portafolio
│   └── transactions.json        # Historial de compras
│
├── 📁 public/
│   ├── index.html               # Dashboard
│   ├── css/
│   │   └── style.css            # Estilos
│   └── js/
│       └── app.js               # Lógica frontend
│
└── 📄 Documentación
    ├── BUFFETT_PRINCIPLES.md    # Principios implementados
    ├── TESTING_GUIDE.md         # Guía de testing
    ├── VALIDATION_ANALYSIS.md   # Análisis de validación
    └── README.md                # Este archivo
```

---

## 🎯 Features

### Dashboard Visual
- ✅ Portafolio actual con distribución
- ✅ Precios en tiempo real (actualizables manualmente)
- ✅ Gráficos de asignación
- ✅ Información de cada activo

### Gestión de Inversiones
- ✅ **Actualizar Precios**: Modifica precios de GEB y TERPEL
- ✅ **Calculadora**: Calcula próxima compra bimestral automáticamente
- ✅ **Registro de Compras**: Guarda historial de todas las compras
- ✅ **Historial**: Ve todas las transacciones realizadas

### Análisis Inteligente
- ✅ **Claude AI Analysis**: Análisis automático del portafolio
- ✅ **Evaluación Buffett**: Valida principios de inversión
- ✅ **Recomendaciones**: Sugiere mejoras basadas en datos

---

## 📚 Documentación

### Para Entender la Estrategia
📖 **[BUFFETT_PRINCIPLES.md](./BUFFETT_PRINCIPLES.md)**
- Principios de Warren Buffett implementados
- Cómo tu portfolio aplica cada principio
- Análisis de moat, margen de seguridad, etc.

### Para Validar los Datos
📖 **[TESTING_GUIDE.md](./TESTING_GUIDE.md)**
- Cómo validar que todo funciona
- Comandos curl para probar APIs
- Checklist de validación completo

### Para Ver Análisis Detallado
📖 **[VALIDATION_ANALYSIS.md](./VALIDATION_ANALYSIS.md)**
- Análisis de cada activo
- Score de cada principio Buffett
- Recomendaciones de optimización

---

## 🔌 API Endpoints

### GET /api/portfolio
Obtiene el portafolio completo
```bash
curl http://localhost:3000/api/portfolio
```

### PUT /api/portfolio/prices
Actualiza el precio de un activo
```bash
curl -X PUT http://localhost:3000/api/portfolio/prices \
  -H "Content-Type: application/json" \
  -d '{"ticker":"GEB","precioActual":3000}'
```

### GET /api/calculadora
Calcula próxima compra bimestral
```bash
curl http://localhost:3000/api/calculadora
```

### POST /api/transactions
Registra una nueva compra
```bash
curl -X POST http://localhost:3000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "fecha":"2026-04-05",
    "activos":[...],
    "comision":14500
  }'
```

### GET /api/transactions
Obtiene historial de compras
```bash
curl http://localhost:3000/api/transactions
```

### POST /api/analyze
Análisis con Claude AI
```bash
curl -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 📊 Datos del Portafolio

### Activos Actuales

#### 🏢 Grupo Energía Bogotá (GEB)
- **Precio**: $2,800
- **Monto**: $170,000 (33%)
- **Yield**: 8.3%
- **Moat**: Concesiones reguladas 50+ años
- **Score Buffett**: 9/10

#### ⛽ Organización Terpel (TERPEL)
- **Precio**: $19,700
- **Monto**: $68,000 (13%)
- **Yield**: 9.2%
- **Moat**: Red física + 80+ años
- **Score Buffett**: 8/10

#### 📈 Titularizadora Colombiana (Bono)
- **Tasa**: 10.4% anual
- **Monto**: $272,000 (54%)
- **Vencimiento**: 2031-04-05
- **Seguridad**: AAA
- **Score Buffett**: 10/10

### Inversión Bimestral
- **Capital disponible**: $850,000
- **Distribución**: 33% GEB + 13% TERPEL + 54% TITULARIZADORA
- **Comisión Tríi**: $14,500 (2.9%)
- **Total invertido**: $510,000 cada 2 meses

### Proyecciones 10 Años
- **Capital invertido**: $30.6M
- **Valor estimado**: $46M
- **Ganancia**: $15.4M
- **Dividendos anuales**: $3.5M (pasivos)

---

## ✅ Principios Buffett Implementados

| Principio | Estado | Details |
|-----------|--------|---------|
| **Circle of Competence** | ✅ | Solo 3 activos simples |
| **Moat Defensible** | ✅ | Todas tienen ventajas competitivas |
| **Margen de Seguridad** | ⚠️ | GEB marginal, TERPEL esperar |
| **Dividend Focus** | ✅ | 9.5% yield promedio |
| **Buy & Hold 10 años** | ✅ | DCA automático |
| **Evita Trampas** | ✅ | No BANCOLOMBIA, no ECOPETROL |
| **Diversificación** | ✅ | 3 activos, riesgo controlado |

**Score Final: 8.5/10** 🎯

---

## 🔐 Configuración de Claude AI

Para usar el análisis automático con Claude AI:

1. **Obtén tu API Key**
   - Ve a https://console.anthropic.com
   - Crea o copia tu API key

2. **Configura el .env**
   ```bash
   cp .env.example .env
   # Edita .env y agrega tu API key
   echo "ANTHROPIC_API_KEY=sk-ant-v4-..." >> .env
   ```

3. **Reinicia el servidor**
   ```bash
   # Presiona Ctrl+C para detener
   node server.js
   ```

4. **Usa en la app**
   - Ve a "Análisis con Claude AI"
   - Click en "🤖 Analizar Portafolio"

---

## 🛠️ Stack Tecnológico

- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Backend**: Node.js + Express.js
- **AI**: Claude API (Haiku 4.5)
- **Datos**: JSON local
- **Puerto**: localhost:3000

---

## 📋 Checklist Inicial

- [ ] `npm install` completado
- [ ] Servidor corriendo en puerto 3000
- [ ] Dashboard carga en http://localhost:3000
- [ ] Puedes ver GEB, TERPEL, TITULARIZADORA
- [ ] Puedes actualizar precios
- [ ] Calculadora funciona
- [ ] Puedes registrar compras
- [ ] (Opcional) Claude AI configurado

---

## 🚀 Próximas Mejoras

### Fase 2 (Próximamente)
- [ ] Gráficos de evolución del portafolio
- [ ] Alertas cuando precio está en "zona Buffett"
- [ ] Sincronización con API real de precios (Yahoo Finance)
- [ ] Exportar reportes PDF
- [ ] Dashboard móvil

### Fase 3
- [ ] Múltiples monedas (COP, USD)
- [ ] Análisis de flujo de caja
- [ ] Simulaciones de escenarios
- [ ] Integración con broker Tríi (automática)

---

## 📧 Soporte

Si tienes dudas:
1. Revisa **TESTING_GUIDE.md** para validación
2. Revisa **VALIDATION_ANALYSIS.md** para análisis detallado
3. Revisa **BUFFETT_PRINCIPLES.md** para entender los principios

---

## 📄 License

Personal use only. Built for John's investment portfolio.

---

**Última actualización**: 2026-04-05  
**Versión**: 1.0.0  
**Estado**: ✅ Listo para usar