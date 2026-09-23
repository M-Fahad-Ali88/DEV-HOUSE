import asyncio
from concurrent.futures import ThreadPoolExecutor

import aiohttp


BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"


async def fetch_page(
    session: aiohttp.ClientSession,
    page_number: int,
) -> str:
    url = BASE_URL.format(page_number)

    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def crawl_pages(
    start_page: int,
    end_page: int,
) -> None:
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_page(session, page_number)
            for page_number in range(start_page, end_page + 1)
        ]

        pages = await asyncio.gather(*tasks)

        for page_number, content in enumerate(
            pages,
            start=start_page,
        ):
            print(
                f"Page {page_number}: "
                f"{len(content)} characters received"
            )


def start_crawler() -> None:
    asyncio.run(crawl_pages(1, 5))


def main() -> None:
    with ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(start_crawler)
        future.result()


if __name__ == "__main__":
    main()