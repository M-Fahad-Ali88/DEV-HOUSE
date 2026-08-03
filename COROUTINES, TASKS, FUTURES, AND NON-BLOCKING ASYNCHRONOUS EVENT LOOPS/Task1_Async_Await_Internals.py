import asyncio

async def fetch_data():
    print("1. Coroutine Started..")
    print("2. Waited for 3 seconds....")

    await asyncio.sleep(3)

    print("3. Coroutine resumed after await..")
    print("4. Fetch Completed...")


async def main():
    print("Main Started")

    coroutine  = fetch_data()
    print(f"Coroutine Object:  , {coroutine}")
    print("Running Coroutine...\n")
    await coroutine
    print("\nMain Finished")

asyncio.run(main())
