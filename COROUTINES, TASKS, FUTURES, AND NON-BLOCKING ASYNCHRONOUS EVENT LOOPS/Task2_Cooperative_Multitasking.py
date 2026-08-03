import asyncio


async def download_file(file_name, delay):
    print(f"{file_name} download started.")

    for i in range(1, 4):
        print(f"{file_name}: Part {i}")
        await asyncio.sleep(delay)

    print(f"{file_name} download completed.\n")


async def main():
    print("Main Started\n")

    task1 = asyncio.create_task(download_file("File A", 1))
    task2 = asyncio.create_task(download_file("File B", 2))
    task3 = asyncio.create_task(download_file("File C", 1.5))

    print("All tasks created.\n")

    await asyncio.gather(task1, task2, task3)

    print("All downloads finished.")


asyncio.run(main())