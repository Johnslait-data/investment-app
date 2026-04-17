# Quick Start Guide

## 1. Start the Dashboard
```bash
streamlit run app.py
```
Opens at: http://localhost:8501

## 2. Navigate Pages
- **📈 Demo Mode**: See example analysis (AAPL, EC, BRK.B pre-loaded)
- **📋 Watchlist**: Add/remove stocks you want to track
- **🔍 Custom Analysis**: Deep dive into one stock's Graham metrics
- **📊 Mi Portafolio**: Track your actual positions with alerts
- **⚠️ Riesgo**: Assess business, financial, and market risk
- **🔌 API Monitor**: Check FMP API quota usage (250 req/day)

## 3. Understanding the Scores

### Investment Score (0-100)
- **≥70**: BUY 🟢 - Strong Graham bargain
- **40-69**: WATCH 🟡 - Monitor for opportunities
- **<40**: AVOID 🔴 - Overvalued or poor fundamentals

### Graham Analysis
| Metric | Graham Target | Your Stock |
|--------|---------------|-----------|
| **P/E Ratio** | ≤15 | Shows your stock's ratio |
| **P/B Ratio** | ≤1.5 | Shows your stock's ratio |
| **Graham Number** | Price should be BELOW this | Calculated from EPS & Book Value |
| **NCAV** | Buy if Price ≤ 67% of NCAV | Margin of Safety metric |

### Example: AAPL
- Current Price: $263.40
- Graham Number: $32.78
- **Status**: ❌ Trading at 8x Graham Number (NOT a buy)

### Example: EC (Mock)
- Current Price: $13.50
- Graham Number: $21.13
- **Status**: ❌ Trading above Graham Number (NOT a buy)

## 4. Key Metrics Explained

**Current Ratio** ≥1.5
- Can the company pay short-term debts?
- ≥1.5 = Healthy
- <1.0 = Liquidity concerns

**Debt/Equity** ≤1.0
- Is the company overleveraged?
- ≤1.0 = Healthy
- >2.0 = High financial risk

**ROE** (Return on Equity) ≥10%
- How efficiently using shareholder money?
- 10-15% = Good
- 15%+ = Excellent
- <5% = Concerning

**Altman Z-Score**
- Bankruptcy risk predictor
- >3.0 = Safe zone
- 1.8-3.0 = Gray zone
- <1.8 = High risk

## 5. Adding a Stock

### To Your Watchlist
1. Go to **📋 Watchlist**
2. Enter ticker (e.g., `AAPL`, `EC`, `JPM`)
3. Click "Add"
4. Wait for data load (FMP API or cache)

### To Your Portfolio
1. Go to **📊 Mi Portafolio**
2. Tab: ➕ **Agregar Posición**
3. Enter: Ticker, Entry Price, Target, Stop Loss
4. System calculates Graham metrics automatically
5. Sets alerts for target/stop loss hits

## 6. Common Tickers

### US Large Cap (S&P 500)
- `AAPL` - Apple
- `MSFT` - Microsoft
- `JNJ` - Johnson & Johnson
- `JPM` - JPMorgan Chase
- `BRK.B` - Berkshire Hathaway
- `WMT` - Walmart

### Colombian (LATAM) - Via ADR
- `EC` - Ecopetrol (Energy) - *Note: Uses mock data*
- `CIB` - Bancolombia (Banking) - *May have limited FMP data*

### Banks
- `JPM` - JPMorgan Chase
- `BAC` - Bank of America
- `WFC` - Wells Fargo

## 7. Understanding Risk Scoring

### Business Risk (Competitive Position)
- **Leader**: Apple in smartphones = LOW risk
- **Competitive**: Generic sector = MEDIUM risk
- **Weak**: Struggling industry = HIGH risk

### Financial Risk
- D/E Ratio >2.0 = HIGH
- Current Ratio <1.0 = HIGH
- ROE <5% = HIGH

### Market Risk
- Market cap <$100M = HIGH (liquidity risk)
- 52-week volatility = Pricing risk
- Market sentiment = Timing risk

## 8. API Quota Tracking

**Daily Limit**: 250 requests/day (resets at 00:00 UTC)

### Current Status
- Go to **🔌 API Monitor**
- See: Calls made, Remaining, Usage %

### How to Optimize
1. **First Load**: Uses 5-7 API calls per stock
2. **Subsequent Loads**: Uses cache (0 API calls)
3. **Cache expires**: After 48 hours
4. **Pro Tip**: Add stocks in batches to fill cache

## 9. Data Sources

### Real FMP Data (Free Tier)
- Company profile
- Current quote
- P/E, P/B ratios
- Current ratio, D/E ratio
- Altman Z-Score, Piotroski Score
- Dividend history

### Calculated by System
- Graham Number = √(22.5 × EPS × Book Value)
- Margin of Safety = (Graham # - Price) / Graham #
- Risk Score = (Business + Financial + Market) / 3

### Mock Data (Fallback)
- AAPL, BRK.B, MSFT (test data)
- EC (Colombian - FMP doesn't cover)
- Used when FMP unavailable

## 10. Typical Workflow

### Daily
1. Open Dashboard
2. Check **📊 Mi Portafolio** → 🔔 **Alertas** tab
3. See if any targets/stops triggered
4. Review **📈 Estadísticas** for performance

### Weekly
1. Check **📋 Watchlist** for new opportunities
2. Run **🔍 Custom Analysis** on 2-3 candidates
3. Review **⚠️ Riesgo** assessment

### Monthly
1. Check **🔌 API Monitor** usage
2. Update portfolio with closed trades
3. Review **📈 Estadísticas** → Closed operations

## 11. Troubleshooting

### "No data for ticker"
- Check ticker spelling (case-insensitive)
- FMP doesn't have all stocks (check major US stocks first)
- Try mock data: AAPL, BRK.B, MSFT, EC

### "API limit reached"
- Check **🔌 API Monitor** → calls remaining
- Wait for daily reset (UTC 00:00)
- Use cached tickers meanwhile

### "Ratios showing as N/A"
- FMP free tier has limited coverage
- Check **📋 Watchlist** source column
- Use mock stocks for testing

## 12. Graham's Investment Rules

1. ✅ P/E ≤ 15 × P/B ≤ 1.5 (or product ≤ 22.5)
2. ✅ Current Ratio ≥ 1.5
3. ✅ D/E ≤ 1.0
4. ✅ Trading ≤ 67% of NCAV (ultimate bargain)
5. ✅ Trading < Graham Number (safe margin)
6. ✅ ROE ≥ 10%
7. ✅ EPS growth positive
8. ✅ Dividend payout <50% of earnings

**Your Dashboard Checks All of These Automatically**

---

## Questions?

- **How to export data?**: Not yet - plan future CSV export
- **How to backtest?**: Not yet - need historical price data
- **Multiple portfolios?**: Save position data manually for now
- **Real-time alerts?**: Run dashboard, check alerts tab daily

---

## Key Takeaway

> "It is far better to buy a wonderful company at a fair price than a fair company at a wonderful price." - Charlie Munger (echoing Graham)

The dashboard helps you find **wonderful companies at wonderful (fair) prices** by:
1. ✅ Screening by Graham metrics
2. ✅ Validating data quality
3. ✅ Assessing risk properly
4. ✅ Tracking positions with alerts
5. ✅ Measuring performance over time
