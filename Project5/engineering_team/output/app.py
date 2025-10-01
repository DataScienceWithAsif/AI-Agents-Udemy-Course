from accounts import Account
import gradio as gr

# Initialize a global account instance
account = None

def create_account(initial_deposit):
    global account
    account = Account(id=1, initial_deposit=initial_deposit)
    return f"Account created with initial deposit: ${initial_deposit}"

def deposit_funds(amount):
    if account is None:
        return "Please create an account first."
    account.deposit(amount)
    return f"Deposited: ${amount}. New Balance: ${account.balance}"

def withdraw_funds(amount):
    if account is None:
        return "Please create an account first."
    if account.withdraw(amount):
        return f"Withdrew: ${amount}. New Balance: ${account.balance}"
    return "Withdrawal amount exceeds balance."

def buy_shares(symbol, quantity):
    if account is None:
        return "Please create an account first."
    if account.buy_shares(symbol, quantity):
        return f"Bought {quantity} shares of {symbol}."
    return "Purchase failed: Check balance or quantity."

def sell_shares(symbol, quantity):
    if account is None:
        return "Please create an account first."
    if account.sell_shares(symbol, quantity):
        return f"Sold {quantity} shares of {symbol}."
    return "Sale failed: Check holdings or quantity."

def report_holdings():
    if account is None:
        return "Please create an account first."
    return account.report_holdings()

def portfolio_value():
    if account is None:
        return "Please create an account first."
    return f"Total Portfolio Value: ${account.portfolio_value()}"

def profit_or_loss():
    if account is None:
        return "Please create an account first."
    return f"Profit/Loss: ${account.profit_or_loss()}"

def transaction_history():
    if account is None:
        return "Please create an account first."
    return account.transaction_history()

with gr.Blocks() as demo:
    gr.Markdown("# Trading Simulation Account Management")

    with gr.Row():
        initial_deposit = gr.Number(label="Initial Deposit", value=1000)
        create_button = gr.Button("Create Account")
    
    create_button.click(create_account, inputs=initial_deposit, outputs="output")

    with gr.Row():
        deposit_amount = gr.Number(label="Deposit Amount")
        deposit_button = gr.Button("Deposit Funds")
    
    deposit_button.click(deposit_funds, inputs=deposit_amount, outputs="output")

    with gr.Row():
        withdraw_amount = gr.Number(label="Withdraw Amount")
        withdraw_button = gr.Button("Withdraw Funds")
    
    withdraw_button.click(withdraw_funds, inputs=withdraw_amount, outputs="output")

    with gr.Row():
        buy_symbol = gr.Textbox(label="Symbol (e.g., AAPL)")
        buy_quantity = gr.Number(label="Quantity")
        buy_button = gr.Button("Buy Shares")
    
    buy_button.click(buy_shares, inputs=[buy_symbol, buy_quantity], outputs="output")

    with gr.Row():
        sell_symbol = gr.Textbox(label="Symbol (e.g., AAPL)")
        sell_quantity = gr.Number(label="Quantity")
        sell_button = gr.Button("Sell Shares")
    
    sell_button.click(sell_shares, inputs=[sell_symbol, sell_quantity], outputs="output")

    with gr.Row():
        holdings_button = gr.Button("Report Holdings")
        portfolio_button = gr.Button("Portfolio Value")
        profit_loss_button = gr.Button("Profit/Loss")
        transaction_button = gr.Button("Transaction History")

    holdings_button.click(report_holdings, outputs="output")
    portfolio_button.click(portfolio_value, outputs="output")
    profit_loss_button.click(profit_or_loss, outputs="output")
    transaction_button.click(transaction_history, outputs="output")

    output = gr.Textbox(label="Output", interactive=False)

demo.launch()