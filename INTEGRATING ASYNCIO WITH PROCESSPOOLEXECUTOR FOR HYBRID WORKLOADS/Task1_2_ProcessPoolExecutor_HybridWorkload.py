import asyncio
from concurrent.futures import ProcessPoolExecutor


def parse_telemetry_data(data):
    print(f"[PROCESS] Started parsing: {data}")

    total = 0
    for i in range(30_000_000):
        total += i

    print(f"[PROCESS] Finished parsing: {data}")

    return f"Parsed -> {data}"


async def receive_network_data(loop, executor):
    telemetry_packets = [
        "TEMP=30,HUM=60",
        "TEMP=31,HUM=62",
        "TEMP=32,HUM=64",
        "TEMP=33,HUM=65"
    ]

    tasks = []

    for packet in telemetry_packets:
        print(f"[EVENT LOOP] Received: {packet}")

        future = loop.run_in_executor(
            executor,
            parse_telemetry_data,
            packet
        )

        tasks.append(future)

        await asyncio.sleep(1)

    results = await asyncio.gather(*tasks)

    print("\n----- Parsed Results -----")

    for result in results:
        print(result)


async def main():
    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor() as executor:
        await receive_network_data(loop, executor)


if __name__ == "__main__":
    asyncio.run(main())