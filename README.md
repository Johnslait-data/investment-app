# 📈 Investment Analyzer — Graham Entrepreneurial Dashboard

A Python-based investment analysis tool that applies Benjamin Graham's principles to identify undervalued stocks for the entrepreneurial investor.

## 🎯 Purpose

This system analyzes stocks using Graham's proven principles:
- **NCAV (Net Current Asset Value)** — True bargains at ≤67% of NCAV
- **Graham Number** — √(22.5 × EPS × Book Value) for intrinsic value
- **Margin of Safety** — Minimum 30% discount to intrinsic value
- **Fundamental Strength** — P/E ≤15, P/B ≤1.5, healthy liquidity, low debt

**Investment Score: 0-100**
- 🟢 **70+**: BUY (strong candidate)
- 🟡 **40-69**: WATCH (monitor, needs better price)
- 🔴 **<40**: AVOID (too expensive or weak fundamentals)

## 📦 Project Structure

```
investment-app/
├── app.py                    # Streamlit dashboard entry point
├── config.py                 # Settings & Graham thresholds
├── demo.py                   # Quick demo script
├── requirements.txt          # Dependencies
├── .env                      # API keys & config
│
├── data/
│   ├── fetcher.py           # yfinance data retrieval
│   ├── cache.py             # SQLite caching layer
│   └── watchlist.json       # User's watchlist
│
├── analysis/
│   ├── graham.py            # Graham Number, NCAV calculations
│   ├── fundamentals.py      # Standard ratios (P/E, P/B, D/E, etc.)
│   └── scoring.py           # 0-100 scoring system
│
└── tests/
    ├── test_graham.py       # Unit tests (12 passing)
    └── test_backtesting.py  # Historical validation (5 passing)
```

## 🚀 Quick Start

### 1. Setup Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install streamlit
```

### 2. Configure API Keys

```bash
# Edit .env file with your API keys (optional, for advanced features)
ANTHROPIC_API_KEY=your_key_here
FMP_API_KEY=your_key_here
```

### 3. Run Dashboard

```bash
# Start Streamlit dashboard
streamlit run app.py
```

Dashboard opens at: **http://localhost:8501**

### 4. Quick Demo (No UI)

```bash
# Run demo without Streamlit
python3 demo.py
```

Output shows:
- Stock fetching from yfinance
- Graham Number calculation
- Fundamental metrics
- 52-week price range

## 📊 Features

### Dashboard Pages

**1. 📋 Watchlist**
- Add/remove tickers
- View all stocks with key metrics
- Quick reference table (P/E, P/B, Current Ratio)

**2. 🔍 Stock Details**
- Deep analysis of individual stocks
- Graham metrics (Graham Number, NCAV, Margin of Safety)
- Fundamental ratios
- 52-week price range

**3. ⚖️ Compare Stocks**
- Side-by-side comparison (up to 4 stocks)
- Comparative metrics table

## ✅ Testing & Validation

### Unit Tests (12/12 Passing)

```bash
source venv/bin/activate
python3 -m pytest tests/test_graham.py -v
```

Tests cover:
- Graham Number formula
- NCAV calculation
- Margin of Safety
- Bargain detection
- Edge cases (zero values, invalid inputs)

### Backtesting (5/5 Passing)

```bash
python3 -m pytest tests/test_backtesting.py -v
```

Historical validation shows:
- ✅ **AAPL March 2020** @ $54 → System said BUY → Reached $232 (+330%)
- ✅ **BRK.B Oct 2022** @ $310 → System said WATCH → Reached $430+ (+39%)
- ✅ **MSFT 2024** @ $425 → System said AVOID (overvalued) → Correctly identified

## 📈 Graham Metrics Explained

### Graham Number

```
Graham Number = √(22.5 × EPS × Book Value Per Share)
```

Graham's formula for "fair value." Buy when price < Graham Number.

### NCAV (Net Current Asset Value)

```
NCAV = (Current Assets - Total Liabilities) / Shares Outstanding
```

The most conservative valuation. Graham's rule: **Buy at ≤67% of NCAV** for maximum margin of safety.

### Margin of Safety

```
MOS = (Intrinsic Value - Current Price) / Intrinsic Value
```

The discount you get buying below intrinsic value. Graham wanted ≥30%.

### Key Ratios

| Metric | Threshold | Meaning |
|--------|-----------|---------|
| **P/E Ratio** | ≤ 15 | Not overpaying for earnings |
| **P/B Ratio** | ≤ 1.5 | Not overpaying for assets |
| **Current Ratio** | ≥ 1.5 | Healthy short-term liquidity |
| **D/E Ratio** | ≤ 1.0 | Conservative debt levels |
| **ROE** | ≥ 10% | Profitable business |

## 🎓 About Graham's Entrepreneurial Investor

Benjamin Graham distinguished two investor profiles:

- **Defensive Investor**: Wants stability, dividends, minimal time; very strict criteria
- **Entrepreneurial Investor**: Willing to do research, seeks bargains; our focus

This system targets the **Entrepreneurial Investor** who:
- Seeks undervalued stocks (NCAV, discounts to intrinsic value)
- Has time to research and monitor
- Can tolerate volatility for upside potential
- Values margin of safety above all

## 📚 References

- **"The Intelligent Investor"** by Benjamin Graham (4th Edition & Revised)
- **"Security Analysis"** by Benjamin Graham & David Dodd
- Graham's principles: Value investing, margin of safety, fundamental analysis

## 🔧 Development

### Adding New Stocks

Edit `data/watchlist.json`:
```json
{
  "tickers": ["AAPL", "BRK.B", "EC", "IBM"]
}
```

### Modifying Graham Thresholds

Edit `config.py`:
```python
GRAHAM_CONFIG = {
    "pe_threshold": 15,           # Change P/E limit
    "pb_threshold": 1.5,          # Change P/B limit
    "ncav_threshold": 0.67,       # Change NCAV discount %
    "margin_of_safety": 0.30,     # Change MOS minimum
    # ...
}
```

### Custom Scoring

Edit `analysis/scoring.py` to adjust point allocation for different metrics.

## 🐛 Troubleshooting

**"ModuleNotFoundError: No module named 'yfinance'"**
```bash
source venv/bin/activate
pip install yfinance
```

**"Could not fetch data for ticker"**
- Ticker may be invalid or temporarily unavailable
- Check yfinance directly: `import yfinance as yf; print(yf.Ticker("AAPL").info)`

**"Connection refused" on localhost:8501**
- Make sure you ran `streamlit run app.py`
- Check if port 8501 is already in use

## 📝 License

Open source educational project for investment analysis practice.

## 🤝 Contributing

To extend this system:
1. Add new analysis modules in `analysis/`
2. Add tests in `tests/`
3. Run full test suite: `pytest tests/ -v`
4. Update README with changes

---

**Happy investing! Remember: "It is far better to buy a wonderful company at a fair price than a fair company at a wonderful price." — Benjamin Graham**
