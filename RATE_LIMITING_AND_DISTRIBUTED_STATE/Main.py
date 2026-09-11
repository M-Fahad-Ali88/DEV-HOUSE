from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from RateLimiter import LIMIT, WINDOW, rate_limiter

app = FastAPI()


@app.middleware("http")
async def rate_limit_headers(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception:
        raise

    rate_limit = getattr(request.state, "rate_limit", None)

    if rate_limit:
        response.headers["X-RateLimit-Limit"] = str(
            rate_limit["limit"]
        )
        response.headers["X-RateLimit-Remaining"] = str(
            rate_limit["remaining"]
        )
        response.headers["X-RateLimit-Reset"] = str(
            rate_limit["reset"]
        )
    else:
        response.headers["X-RateLimit-Limit"] = str(LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(LIMIT)
        response.headers["X-RateLimit-Reset"] = str(WINDOW)

    return response


@app.exception_handler(429)
async def rate_limit_exception_handler(
    request: Request,
    exc
):
    rate_limit = getattr(
        request.state,
        "rate_limit",
        {
            "limit": LIMIT,
            "remaining": 0,
            "reset": WINDOW
        }
    )

    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded"
        },
        headers={
            "X-RateLimit-Limit": str(rate_limit["limit"]),
            "X-RateLimit-Remaining": str(rate_limit["remaining"]),
            "X-RateLimit-Reset": str(rate_limit["reset"])
        }
    )


@app.get("/")
def home(
    request: Request,
    rate_limit=Depends(rate_limiter)
):
    return {
        "message": "Request allowed",
        "rate_limit": rate_limit
    }