import time
import httpx

from fastapi import FastAPI

app = FastAPI()


@app.get("/httpx")
async def httpx_endpoint():
    start_time = time.perf_counter()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://example.com",
            timeout=10.0
        )

    elapsed_time = time.perf_counter() - start_time

    return {
        "message": "Non-blocking HTTP request completed",
        "status_code": response.status_code,
        "time_taken": round(elapsed_time, 2)
    }