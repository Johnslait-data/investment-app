from pydantic import BaseModel

class Transaction(BaseModel):
    id: int
    portfolio_id: int
    asset: str
    amount: float
    type: str  # buy or sell
    date: str
