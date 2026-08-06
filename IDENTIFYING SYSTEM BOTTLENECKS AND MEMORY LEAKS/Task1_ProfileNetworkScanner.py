import asyncio
import cProfile
import pstats

async def run_network_scanner():
    await asyncio.sleep(2)

def main():
    asyncio.run(run_network_scanner())

if __name__ == "__main__":
    profiler = cProfile.Profile()

    profiler.enable()

    main()

    profiler.disable()

    print("=" * 60)
    print("NETWORK SCANNER PERFORMANCE REPORT")
    print("=" * 60)

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumtime")
    stats.print_stats(20)