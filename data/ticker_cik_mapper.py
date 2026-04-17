"""
Mapper de Ticker a CIK (SEC Identifier)
Usado para FMP stable endpoints que requieren CIK
"""

# Common US stock tickers to CIK mapping
TICKER_TO_CIK = {
    # Tech
    "AAPL": "0000320193",  # Apple
    "MSFT": "0000789019",  # Microsoft
    "GOOGL": "0001018724",  # Alphabet (Google)
    "GOOG": "0001018724",   # Alphabet (Google) Class C
    "AMZN": "0001018724",   # Amazon - TEMP
    "NVDA": "0001045810",   # NVIDIA
    "META": "0001326801",   # Meta (Facebook)
    "TSLA": "0001652044",   # Tesla
    "INTC": "0000050104",   # Intel

    # Finance
    "BRK.A": "0001067983",  # Berkshire Hathaway A
    "BRK.B": "0001067983",  # Berkshire Hathaway B
    "JPM": "0000019617",    # JPMorgan Chase
    "BAC": "0000070858",    # Bank of America
    "WFC": "0000072971",    # Wells Fargo
    "GS": "0000886676",     # Goldman Sachs

    # Energy (Colombia/Latam)
    "EC": "0001046582",     # Ecopetrol ADR

    # Healthcare
    "JNJ": "0000200406",    # Johnson & Johnson
    "PFE": "0000078003",    # Pfizer
    "MRK": "0000310158",    # Merck
    "ABBV": "0001551152",   # AbbVie

    # Consumer
    "KO": "0000021344",     # Coca-Cola
    "PEP": "0000884996",    # PepsiCo
    "WMT": "0000104169",    # Walmart
    "COST": "0000909832",   # Costco

    # Industrial
    "BA": "0000012927",     # Boeing
    "CAT": "0000018230",    # Caterpillar
    "GE": "0000040545",     # General Electric
}

def get_cik(ticker: str) -> str:
    """
    Get CIK from ticker

    Args:
        ticker: Stock ticker (e.g., 'AAPL')

    Returns:
        CIK string (e.g., '0000320193')
    """
    return TICKER_TO_CIK.get(ticker.upper())

def has_cik(ticker: str) -> bool:
    """Check if we have CIK for this ticker"""
    return ticker.upper() in TICKER_TO_CIK

def add_cik(ticker: str, cik: str):
    """Add or update a ticker->CIK mapping"""
    TICKER_TO_CIK[ticker.upper()] = cik
