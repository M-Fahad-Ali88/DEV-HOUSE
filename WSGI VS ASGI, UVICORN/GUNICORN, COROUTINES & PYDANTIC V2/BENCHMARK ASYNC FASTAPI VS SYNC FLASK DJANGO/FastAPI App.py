import asyncio
import threading

from fastapi import FastAPI

app = FastAPI()


@app.get("/async")
async def async_endpoint():
    await asyncio.sleep(1)

    return {
        "framework": "FastAPI",
        "type": "asynchronous",
        "thread": threading.current_thread().name
    }