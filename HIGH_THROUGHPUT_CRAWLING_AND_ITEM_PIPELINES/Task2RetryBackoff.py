import asyncio

import aiohttp


URL = "https://books.toscrape.com/"
MAX_RETRIES = 3
BASE_DELAY = 1


async def fetch_with_retry(
    session: aiohttp.ClientSession,
) -> str:
    for attempt in range(MAX_RETRIES + 1):
        try:
            async with session.get(
                URL,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:

                if response.status in (429, 503):
                    if attempt == MAX_RETRIES:
                        response.raise_for_status()

                    delay = BASE_DELAY * (2 ** attempt)

                    print(
                        f"HTTP {response.status}. "
                        f"Retrying in {delay}s..."
                    )

                    await asyncio.sleep(delay)
                    continue

                response.raise_for_status()

                print("Request successful.")
                return await response.text()

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
        ) as error:

            if attempt == MAX_RETRIES:
                print("Maximum retries reached.")
                raise error

            delay = BASE_DELAY * (2 ** attempt)

            print(
                f"{type(error).__name__}. "
                f"Retrying in {delay}s..."
            )

            await asyncio.sleep(delay)

    raise RuntimeError("Request failed.")


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        content = await fetch_with_retry(session)

        print(f"Received {len(content)} characters.")


if __name__ == "__main__":
    asyncio.run(main())