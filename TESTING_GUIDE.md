# Guía de Testing - Cómo Validar tu Portfolio App

## 1️⃣ Abre la App

```
Abre tu navegador y ve a: http://localhost:3000
```

**Deberías ver:**
- Header azul con "📊 Portfolio Inversión Colombia 2026"
- Tarjetas con GEB, TERPEL, Titularizadora
- Gráficos de distribución
- Botones para interactuar

---

## 2️⃣ Valida los Datos del Portfolio

### ¿Qué datos ve la app?

**GET /api/portfolio** → Los datos vienen de `data/portfolio.json`

```bash
# En terminal, prueba esto:
curl http://localhost:3000/api/portfolio | jq .
```

**Deberías ver:**
```json
{
  "meta": {
    "usuario": "John",
    "capitalInicial": 825000,
    "aporteBimestral": 850000,
    "horizonteTiempo": "10 años"
  },
  "activos": {
    "GEB": {
      "nombre": "Grupo Energía Bogotá",
      "precioActual": 2800,
      "monto": 170000,
      "porcentaje": 33,
      "dividendYield": 8.3,
      "moat": "Concesiones reguladas",
      "precioJusto": "3200-3500",
      "accion": "COMPRA"
    }
    // ... TERPEL, TITULARIZADORA
  }
}
```

---

## 3️⃣ Prueba: Actualizar un Precio

### En la app:
1. Click en **"Actualizar Precio"** en la tarjeta de GEB
2. Ingresa nuevo precio: `3000`
3. Click **"Guardar"**

### ¿Qué pasa?
- El precio cambia en pantalla
- Se guarda en `data/portfolio.json`
- El modal se cierra

### Valida con curl:
```bash
curl -X PUT http://localhost:3000/api/portfolio/prices \
  -H "Content-Type: application/json" \
  -d '{"ticker":"GEB","precioActual":3000}'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "ticker": "GEB",
  "precioAnterior": 2800,
  "precioActual": 3000,
  "mensaje": "Precio de GEB actualizado"
}
```

Luego ve a `data/portfolio.json` y verifica que cambió.

---

## 4️⃣ Prueba: Calcular Próxima Compra

### En la app:
1. Ve a sección "Calculadora Próxima Compra"
2. Click **"Calcular"**

### ¿Qué deberías ver?
```
📋 Próxima Compra Bimestral

Capital Disponible: $850,000

Distribución:
  GEB: [cantidad] acciones × $[precio] = $170,000
  TERPEL: [cantidad] acciones × $[precio] = $68,000
  TITULARIZADORA: $272,000 @ 10.4%

Comisión Tríi: -$14,500
Total Neto: $495,500
```

### Valida manualmente:
- Capital bimestral: **$850,000** ✓
- GEB monto: **$170,000** (33%) ✓
- TERPEL monto: **$68,000** (13%) ✓
- TITULARIZADORA: **$272,000** (54%) ✓
- Comisión: **$14,500** (2.9%) ✓
- Total: **$510,000** invertido ✓

Con curl:
```bash
curl http://localhost:3000/api/calculadora | jq .
```

---

## 5️⃣ Prueba: Registrar una Compra

### En la app:
1. Click en **"✅ Registrar Compra"** (después de calcular)
2. La transacción se guarda automáticamente

### Verifica en transacciones:
- La compra aparece en "Historial de Compras"
- Fecha = hoy
- Activos = GEB, TERPEL, TITULARIZADORA

### Valida con curl:
```bash
curl http://localhost:3000/api/transactions | jq .
```

**Deberías ver:**
```json
{
  "transactions": [
    {
      "id": 1,
      "fecha": "2026-04-05",
      "tipo": "compra",
      "activos": [...],
      "comision": 14500,
      "totalNeto": 495500
    },
    {
      "id": 2,  // Nueva compra
      "fecha": "2026-04-05",
      "tipo": "compra",
      "activos": [...],
      "comision": 14500,
      "totalNeto": 495500
    }
  ]
}
```

---

## 6️⃣ Prueba: Análisis con Claude AI

### Requisito:
- Necesitas configurar tu **ANTHROPIC_API_KEY**

### Setup:
1. Ve a [console.anthropic.com](https://console.anthropic.com)
2. Copia tu API key
3. Crea archivo `.env` en la raíz:
   ```
   ANTHROPIC_API_KEY=sk-ant-v4-xxxxx
   ```
4. Reinicia servidor: `Control+C` y `node server.js`

### En la app:
1. Ve a "Análisis con Claude AI"
2. Click **"🤖 Analizar Portafolio"**
3. Espera respuesta (5-10 segundos)

### ¿Qué recibirás?
Claude analizará:
- Evaluación de asignación actual
- Análisis de diversificación
- Comentarios sobre dividend yield
- Recomendaciones próxima compra
- Riesgos y mitigación

Ejemplo respuesta:
```
Tu asignación del 54% en renta fija (Titularizadora) es 
conservadora pero apropiada para un horizonte de 10 años.

GEB con yield 8.3% es interesante, pero el 14% de margen 
de seguridad es bajo. Espera a $2,000-2,200 para mejor 
oportunidad.

TERPEL sin margen - considera pequeña posición ahora y 
esperar caída.

El bono a 10.4% es excelente para ancla de seguridad...
```

### Valida con curl:
```bash
curl -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 7️⃣ Cómo se Aplican los Principios Buffett

### En tu app, puedes verificar:

#### ✅ Margen de Seguridad
```json
// data/portfolio.json
"GEB": {
  "precioActual": 2800,
  "precioJusto": "3200-3500",
  "margen": "14-25%",  // Buffett requiere 20%+
}
```

#### ✅ Moat Defensible
```json
"GEB": {
  "moat": "Concesiones reguladas",
  "durabilidad": "50+ años"
}
"TERPEL": {
  "moat": "Red física + 80+ años de operación"
}
```

#### ✅ Circle of Competence
En el dashboard, cada activo tiene:
- Explicación del negocio
- Razón de compra
- Métricas clave

#### ✅ Evita Trampas
En `data/portfolio.json` está la lista de qué **NO comprar**:
- BANCOLOMBIA: Sobrevaluada +110%
- ISA: Sin margen, en máximo
- ECOPETROL: Commodity puro

---

## 8️⃣ Checklist de Validación

- [ ] Dashboard carga en http://localhost:3000
- [ ] Ve datos correctos de GEB, TERPEL, TITULARIZADORA
- [ ] Puede actualizar precio de GEB → se guarda en JSON
- [ ] Calculadora muestra $510,000 total (3 activos)
- [ ] Puede registrar compra → aparece en historial
- [ ] (Opcional) Análisis Claude AI funciona
- [ ] Distribución de barras: 33% + 13% + 54% = 100%
- [ ] Dividends yields se muestran correctamente

---

## 9️⃣ Cómo Ver los Datos Crudos

### Ver portfolio.json:
```bash
cat data/portfolio.json | jq .
```

### Ver transactions.json:
```bash
cat data/transactions.json | jq .
```

### Ver logs del servidor:
Mira la terminal donde corre `node server.js`

---

## 🔟 Si Algo no Funciona

### App no carga:
```bash
# Verifica que servidor esté corriendo
curl http://localhost:3000/api/portfolio
```

### Precio no se actualiza:
```bash
# Verifica que el archivo se esté guardando
cat data/portfolio.json | grep -A2 precioActual
```

### API key para Claude no funciona:
```bash
# Verifica que .env exista y esté en la raíz
cat .env
# Debe mostrar: ANTHROPIC_API_KEY=tu_key
```

---

## Conclusión

Una vez valides todo lo anterior, **sabrás que:**
- ✅ Datos se guardan correctamente
- ✅ APIs funcionan
- ✅ Frontend se actualiza
- ✅ Principios Buffett están implementados
- ✅ Claude AI analiza tu portfolio

¡Listo para invertir! 🎯
