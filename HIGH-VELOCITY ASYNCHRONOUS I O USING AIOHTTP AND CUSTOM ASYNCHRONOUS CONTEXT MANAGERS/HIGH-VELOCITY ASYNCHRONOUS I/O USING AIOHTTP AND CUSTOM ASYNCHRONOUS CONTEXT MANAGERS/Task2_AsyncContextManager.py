#Purpose: Implement custom asynchronous context managers (__aenter__, __aexit__) for safe resource management.

import asyncio
class Connection:
    async def __aenter__(self):
        print("Connection Opened")
        return self
    async def __aexit__(self, exc_type, exc, tb):
        print("Connection Closed")

    async def send(self):
        print("Sending Data")
        await asyncio.sleep(1)
        print("Data Sent")

async def main():
    async with Connection() as conn:
        await conn.send()
asyncio.run(main())
