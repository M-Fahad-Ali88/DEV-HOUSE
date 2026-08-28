from fastapi import FastAPI

app = FastAPI(
    title="Event Analytics API Gateway",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "service": "Event Analytics API Gateway",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }