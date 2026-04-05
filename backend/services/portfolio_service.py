from models.portfolio import Portfolio
from backend.models.transaction import Transaction
from typing import List

# Dummy in-memory storage for demonstration
portfolios: List[Portfolio] = []
transactions: List[Transaction] = []

def get_portfolios() -> List[Portfolio]:
    return portfolios

def add_portfolio(portfolio: Portfolio):
    portfolios.append(portfolio)

def get_transactions() -> List[Transaction]:
    return transactions

def add_transaction(transaction: Transaction):
    transactions.append(transaction)
