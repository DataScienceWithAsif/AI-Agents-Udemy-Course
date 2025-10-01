class Account:
    def __init__(self, id: int, initial_deposit: float) -> None:
        self.id = id
        self.balance = initial_deposit
        self.initial_deposit = initial_deposit
        self.holdings = {}
        self.transactions = []

    def deposit(self, amount: float) -> None:
        if amount > 0:
            self.balance += amount
            self.transactions.append({'type': 'deposit', 'amount': amount})

    def withdraw(self, amount: float) -> bool:
        if amount > 0 and amount <= self.balance:
            self.balance -= amount
            self.transactions.append({'type': 'withdraw', 'amount': amount})
            return True
        return False

    def buy_shares(self, symbol: str, quantity: int) -> bool:
        cost = get_share_price(symbol) * quantity
        if quantity > 0 and cost <= self.balance:
            self.balance -= cost
            if symbol in self.holdings:
                self.holdings[symbol] += quantity
            else:
                self.holdings[symbol] = quantity
            self.transactions.append({'type': 'buy', 'symbol': symbol, 'quantity': quantity})
            return True
        return False

    def sell_shares(self, symbol: str, quantity: int) -> bool:
        if symbol in self.holdings and quantity > 0 and quantity <= self.holdings[symbol]:
            revenue = get_share_price(symbol) * quantity
            self.balance += revenue
            self.holdings[symbol] -= quantity
            if self.holdings[symbol] == 0:
                del self.holdings[symbol]
            self.transactions.append({'type': 'sell', 'symbol': symbol, 'quantity': quantity})
            return True
        return False

    def portfolio_value(self) -> float:
        total_value = self.balance
        for symbol, quantity in self.holdings.items():
            total_value += get_share_price(symbol) * quantity
        return total_value

    def profit_or_loss(self) -> float:
        return self.portfolio_value() - self.initial_deposit

    def report_holdings(self) -> dict:
        return self.holdings

    def transaction_history(self) -> list:
        return self.transactions

def get_share_price(symbol: str) -> float:
    prices = {'AAPL': 150.0, 'TSLA': 700.0, 'GOOGL': 2700.0}
    return prices.get(symbol, 0.0)