from pydantic import BaseModel
from typing import List, Optional

class Portfolio(BaseModel):
    id: int
    name: str
    owner: str
    transactions: Optional[List[int]] = []

class Transaction(BaseModel):
    id: int
    portfolio_id: int
    asset: str
    amount: float
    type: str  # buy or sell
    date: str
