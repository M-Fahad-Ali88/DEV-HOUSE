import asyncio
import time


async def task1():
    for i in range(1, 6):
        print(f"Task 1 -> {i}")
        time.sleep(1)

    print("Task 1 Completed\n")


async def task2():
    for i in range(1, 6):
        print(f"Task 2 -> {i}")
        await asyncio.sleep(1)

    print("Task 2 Completed\n")


async def main():
    print("Main Started\n")

    task_1 = asyncio.create_task(task1())
    task_2 = asyncio.create_task(task2())

    await asyncio.gather(task_1, task_2)

    print("Main Finished")


asyncio.run(main())