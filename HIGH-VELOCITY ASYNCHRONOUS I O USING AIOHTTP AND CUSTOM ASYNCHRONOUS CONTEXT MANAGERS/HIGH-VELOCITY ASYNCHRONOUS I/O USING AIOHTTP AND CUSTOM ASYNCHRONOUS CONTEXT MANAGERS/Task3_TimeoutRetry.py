#Purpose: Design deterministic timeout and retry mechanisms.import aiohttp
import asyncio
import aiohttp

URL = "https://jsonplaceholder.typicode.com/posts/1"
MAX_RETRIES = 3
TIMEOUT_SECONDS = 0.001


async def fetch_data(session):
    async with session.get(URL) as response:
        response.raise_for_status()
        return await response.json()


async def main():
    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"Attempt {attempt}")

                data = await fetch_data(session)

                print("Request successful")
                print(data)
                break

            except asyncio.TimeoutError:
                print("Request timed out")

            except aiohttp.ClientError as error:
                print(f"Network error: {error}")

            if attempt < MAX_RETRIES:
                print("Retrying...")
                await asyncio.sleep(1)
            else:
                print("All retry attempts failed")


asyncio.run(main())