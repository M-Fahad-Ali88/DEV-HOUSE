import asyncio
import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/blocking")
async def blocking_endpoint():
    start_time = time.perf_counter()

    time.sleep(5)

    elapsed_time = time.perf_counter() - start_time

    return {
        "message": "Blocking operation completed",
        "time_taken": round(elapsed_time, 2)
    }


@app.get("/normal")
async def normal_endpoint():
    return {
        "message": "Normal endpoint response"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "Blocking_Test:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )