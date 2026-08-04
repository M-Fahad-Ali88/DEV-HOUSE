import aiohttp
import asyncio
import os
import time

api_key = os.getenv("ALPHAVANTAGE_API_KEY")

symbols = ["IBM", "AAPL", "GOOGL", "MSFT", "AMZN","IBM", "AAPL", "GOOGL", "MSFT", "AMZN","IBM", "AAPL", "GOOGL", "MSFT", "AMZN","IBM", "AAPL", "GOOGL", "MSFT", "AMZN"]
results = []


async def fetch_data(session, symbol):
    print(f"Working on symbol {symbol}")

    url = (
        f"https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_INTRADAY"
        f"&symbol={symbol}"
        f"&interval=5min"
        f"&apikey={api_key}"
    )

    async with session.get(url) as response:
        data = await response.json()
        results.append(data)


async def main():
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = []

        for symbol in symbols:
            tasks.append(fetch_data(session, symbol))

        await asyncio.gather(*tasks)

    end_time = time.time()

    print(f"It took {end_time - start_time:.2f} seconds to make {len(symbols)} API calls.")
    print("You did it!")


asyncio.run(main())

