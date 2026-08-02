from portfolio.loader import PortfolioLoader

loader = PortfolioLoader()

symbols = loader.get_symbols()

print()

print("Portfolio Symbols")

print("-" * 50)

for symbol in symbols:
    print(symbol)

print()

print(f"Total Symbols : {len(symbols)}")