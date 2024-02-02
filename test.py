import pandas as pd

from firstrade import account, order, symbols

# Create a session
ft_ss = account.FTSession(username='zheng769', password='z$H@zr3yC$_$P@K', pin='8126',
                          proxies={'https': 'http://127.0.0.1:7890', 'http': 'http://127.0.0.1:7890'})

# Get account data
ft_accounts = account.FTAccountData(ft_ss)
if len(ft_accounts.account_numbers) < 1:
    raise Exception("No accounts found or an error occured exiting...")

# Print ALL account data
print(ft_accounts.all_accounts)

# Print 1st account number.
print(ft_accounts.account_numbers[0])

# Print ALL accounts market values.
print(ft_accounts.account_balances)

# Get quote for INTC
quote = symbols.SymbolQuote(ft_ss, "INTC")
print(f"Symbol: {quote.symbol}")
print(f"Exchange: {quote.exchange}")
print(f"Bid: {quote.bid}")
print(f"Ask: {quote.ask}")
print(f"Last: {quote.last}")
print(f"Change: {quote.change}")
print(f"High: {quote.high}")
print(f"Low: {quote.low}")
print(f"Volume: {quote.volume}")
print(f"Company Name: {quote.company_name}")

# Get positions and print them out for an account.
positions = ft_accounts.get_positions(account=ft_accounts.account_numbers[0])
# for key in ft_accounts.securities_held:
#     print(
#         f"Quantity {ft_accounts.securities_held[key]['quantity']} of security {key} held in account {ft_accounts.account_numbers[1]}"
#     )
print(positions)

# Create an order object.
ft_order = order.Order(ft_ss)

# Place order and print out order confirmation data.
# ft_order.place_orderq(
#     ft_accounts.account_numbers[0],
#     symbol="INTC",
#     price_type=order.PriceType.MARKET,
#     order_type=order.OrderType.BUY,
#     quantity=1,
#     duration=order.Duration.DAY,
#     dry_run=False,
# )

expire_date = pd.Timestamp('2024-02-17 05:00:00', tz='Asia/Shanghai')
ft_order.place_option_order(ft_accounts.account_numbers[0], 'JD', 'BO', 1, expire_date, 22, 'C',
                            0.05, False)

# Print Order data Dict
print(ft_order.order_confirmation)

# Check if order was successful
if ft_order.order_confirmation["success"] == "Yes":
    print("Order placed successfully.")
    # Print Order ID
    print(f"Order ID: {ft_order.order_confirmation['orderid']}.")
else:
    print("Failed to place order.")
    # Print errormessage
    print(ft_order.order_confirmation["actiondata"])
