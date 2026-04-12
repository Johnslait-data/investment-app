from models.transaction import Transaction
from typing import List

# Dummy in-memory storage for demonstration
transactions: List[Transaction] = []

def get_transactions() -> List[Transaction]:
    return transactions

def add_transaction(transaction: Transaction):
    transactions.append(transaction)
