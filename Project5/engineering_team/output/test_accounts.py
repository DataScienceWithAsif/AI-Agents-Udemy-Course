import unittest
from accounts import Account, get_share_price

class TestAccount(unittest.TestCase):

    def setUp(self):
        self.account = Account(id=1, initial_deposit=1000.0)

    def test_initialization(self):
        self.assertEqual(self.account.id, 1)
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.initial_deposit, 1000.0)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(self.account.transactions, [])

    def test_deposit(self):
        self.account.deposit(500.0)
        self.assertEqual(self.account.balance, 1500.0)
        self.assertEqual(len(self.account.transactions), 1)

    def test_withdraw_success(self):
        self.assertTrue(self.account.withdraw(200.0))
        self.assertEqual(self.account.balance, 800.0)
        self.assertEqual(len(self.account.transactions), 1)

    def test_withdraw_insufficient_balance(self):
        self.assertFalse(self.account.withdraw(1200.0))
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(len(self.account.transactions), 0)

    def test_buy_shares_success(self):
        self.account.deposit(500.0)  # Add funds for the purchase
        self.assertTrue(self.account.buy_shares('AAPL', 2))
        self.assertEqual(self.account.balance, 700.0)
        self.assertEqual(self.account.holdings['AAPL'], 2)
        self.assertEqual(len(self.account.transactions), 1)

    def test_buy_shares_insufficient_funds(self):
        self.assertFalse(self.account.buy_shares('AAPL', 100))  # More shares than balance
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(len(self.account.transactions), 0)

    def test_sell_shares_success(self):
        self.account.deposit(500.0)
        self.account.buy_shares('AAPL', 2)  # Buy shares first
        self.assertTrue(self.account.sell_shares('AAPL', 1))
        self.assertEqual(self.account.balance, 850.0)  # 700 + 150
        self.assertEqual(self.account.holdings['AAPL'], 1)
        self.assertEqual(len(self.account.transactions), 2)

    def test_sell_shares_not_owned(self):
        self.assertFalse(self.account.sell_shares('TSLA', 1))
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(len(self.account.transactions), 0)

    def test_portfolio_value(self):
        self.account.deposit(500.0)
        self.account.buy_shares('AAPL', 2)
        self.assertEqual(self.account.portfolio_value(), 700.0 + 300.0)  # 700.0 balance + 300.0 (2 shares of AAPL)

    def test_profit_or_loss(self):
        self.account.deposit(500.0)
        self.account.buy_shares('AAPL', 2)
        self.assertEqual(self.account.profit_or_loss(), 700.0 + 300.0 - 1000.0)

    def test_report_holdings(self):
        self.account.buy_shares('AAPL', 2)
        self.assertEqual(self.account.report_holdings(), {'AAPL': 2})

    def test_transaction_history(self):
        self.account.deposit(500.0)
        self.account.withdraw(100.0)
        self.assertEqual(len(self.account.transaction_history()), 2)

if __name__ == '__main__':
    unittest.main()