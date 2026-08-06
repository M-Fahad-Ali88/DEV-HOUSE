import asyncio
import tracemalloc

async def run_network_scanner():
    await asyncio.sleep(2)

async def main():
    tracemalloc.start()

    snapshot_before = tracemalloc.take_snapshot()

    await run_network_scanner()

    current, peak = tracemalloc.get_traced_memory()

    snapshot_after = tracemalloc.take_snapshot()

    print("=" * 60)
    print("MEMORY USAGE")
    print("=" * 60)
    print(f"Current Memory : {current / 1024:.2f} KB")
    print(f"Peak Memory    : {peak / 1024:.2f} KB")

    print("\nTop 10 Memory Allocations")
    print("-" * 60)

    for stat in snapshot_after.statistics("lineno")[:10]:
        print(stat)

    print("\nMemory Growth")
    print("-" * 60)

    for stat in snapshot_after.compare_to(snapshot_before, "lineno")[:10]:
        print(stat)

    current_task = asyncio.current_task()

    orphan_tasks = [
        task
        for task in asyncio.all_tasks()
        if task is not current_task and not task.done()
    ]

    print("\nAsync Task Check")
    print("-" * 60)

    if orphan_tasks:
        print(f"WARNING: {len(orphan_tasks)} task(s) are still running.")
        for task in orphan_tasks:
            print(task)
    else:
        print("No orphan tasks detected.")

    tracemalloc.stop()

if __name__ == "__main__":
    asyncio.run(main())