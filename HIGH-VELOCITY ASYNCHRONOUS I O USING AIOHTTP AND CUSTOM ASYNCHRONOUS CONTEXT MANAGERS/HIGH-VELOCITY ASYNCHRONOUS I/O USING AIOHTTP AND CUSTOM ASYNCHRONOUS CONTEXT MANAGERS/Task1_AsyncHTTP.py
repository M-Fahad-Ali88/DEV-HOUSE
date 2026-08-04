#Purpose: Build asynchronous HTTP engine interfaces using aiohttp.
import aiohttp
import asyncio

async def fetch():
    url = "https://jsonplaceholder.typicode.com/posts/1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            print(data)
asyncio.run(fetch())
