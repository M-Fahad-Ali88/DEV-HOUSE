import requests
import os
import time

api_key = os.getenv("ALPHAVANTAGE_API_KEY")

symbols = ["IBM", "AAPL", "GOOGL", "MSFT", "AMZN"]
results = []

start_time = time.time()

for symbol in symbols:
    print(f"Working on symbol {symbol}")

    url = (
        f"https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_INTRADAY"
        f"&symbol={symbol}"
        f"&interval=5min"
        f"&apikey={api_key}"
    )

    response = requests.get(url)
    results.append(response.json())

end_time = time.time()

print(f"It took {end_time - start_time:.2f} seconds to make {len(symbols)} API calls.")
print("You did it!")