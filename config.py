"""
Configuration for Investment Analyzer
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CACHE_DB = DATA_DIR / "cache.db"
WATCHLIST_FILE = DATA_DIR / "watchlist.json"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# API Keys (from .env)
from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
FMP_API_KEY = os.getenv("FMP_API_KEY", "")  # Optional

# Graham Parameters
GRAHAM_CONFIG = {
    "pe_threshold": 15,  # P/E ≤ 15
    "pb_threshold": 1.5,  # P/B ≤ 1.5
    "ncav_threshold": 0.67,  # Buy at ≤ 67% of NCAV
    "margin_of_safety": 0.30,  # 30% minimum
    "current_ratio_min": 1.5,
    "debt_equity_max": 1.0,
}

# Scoring Config
SCORING_CONFIG = {
    "ncav_ganga": 30,  # Max points for NCAV deal
    "graham_number": 20,
    "margin_safety": 15,
    "pe_ratio": 10,
    "pb_ratio": 10,
    "current_ratio": 10,
    "debt_equity": 5,
    "total": 100,
}

# Recommendations thresholds
RECOMMENDATIONS = {
    "buy": 70,  # ≥ 70
    "watch": 40,  # 40-69
    "avoid": 0,  # < 40
}
