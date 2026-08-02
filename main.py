from market.fetch_prices import fetch_latest_prices

symbols = [
    "NIFTYBEES",
    "BANKBEES",
    "PHARMABEES",
]

prices = fetch_latest_prices(symbols)

for p in prices:
    print(p)