from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
from config import settings
from models.portfolio import Portfolio
from models.transaction import Transaction
from services import portfolio_service, transaction_service

app = FastAPI(title="Investment Portfolio API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Investment Portfolio API"}

# --- Portfolio Endpoints ---

@app.get("/portfolios", response_model=List[Portfolio])
def list_portfolios():
    return portfolio_service.get_portfolios()

@app.get("/portfolios/{portfolio_id}", response_model=Portfolio)
def get_portfolio(portfolio_id: int):
    for p in portfolio_service.get_portfolios():
        if p.id == portfolio_id:
            return p
    raise HTTPException(status_code=404, detail="Portfolio not found.")

@app.post("/portfolios", response_model=Portfolio, status_code=status.HTTP_201_CREATED)
def create_portfolio(portfolio: Portfolio):
    if not portfolio.name or not portfolio.owner:
        raise HTTPException(status_code=400, detail="Name and owner are required.")
    if any(p.id == portfolio.id for p in portfolio_service.get_portfolios()):
        raise HTTPException(status_code=409, detail="Portfolio with this ID already exists.")
    portfolio_service.add_portfolio(portfolio)
    return portfolio

@app.put("/portfolios/{portfolio_id}", response_model=Portfolio)
def update_portfolio(portfolio_id: int, portfolio: Portfolio):
    portfolios = portfolio_service.get_portfolios()
    for idx, p in enumerate(portfolios):
        if p.id == portfolio_id:
            portfolios[idx] = portfolio
            return portfolio
    raise HTTPException(status_code=404, detail="Portfolio not found.")

@app.delete("/portfolios/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(portfolio_id: int):
    portfolios = portfolio_service.get_portfolios()
    for idx, p in enumerate(portfolios):
        if p.id == portfolio_id:
            del portfolios[idx]
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail="Portfolio not found.")

# --- Transaction Endpoints ---

@app.get("/transactions", response_model=List[Transaction])
def list_transactions():
    return transaction_service.get_transactions()

@app.get("/transactions/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: int):
    for t in transaction_service.get_transactions():
        if t.id == transaction_id:
            return t
    raise HTTPException(status_code=404, detail="Transaction not found.")

@app.post("/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: Transaction):
    if not transaction.asset or transaction.amount is None or not transaction.type:
        raise HTTPException(status_code=400, detail="Asset, amount, and type are required.")
    if transaction.type not in ("buy", "sell"):
        raise HTTPException(status_code=400, detail="Type must be 'buy' or 'sell'.")
    if any(t.id == transaction.id for t in transaction_service.get_transactions()):
        raise HTTPException(status_code=409, detail="Transaction with this ID already exists.")
    transaction_service.add_transaction(transaction)
    return transaction

@app.put("/transactions/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: int, transaction: Transaction):
    transactions = transaction_service.get_transactions()
    for idx, t in enumerate(transactions):
        if t.id == transaction_id:
            transactions[idx] = transaction
            return transaction
    raise HTTPException(status_code=404, detail="Transaction not found.")

@app.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int):
    transactions = transaction_service.get_transactions()
    for idx, t in enumerate(transactions):
        if t.id == transaction_id:
            del transactions[idx]
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail="Transaction not found.")