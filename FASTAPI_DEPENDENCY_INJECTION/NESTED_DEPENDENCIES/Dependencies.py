from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Database import DatabaseSession

security = HTTPBearer()


def validate_api_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials

    if token != "secret-token":
        raise HTTPException(
            status_code=401,
            detail="Invalid API token"
        )

    return token


def get_database(
    token: str = Depends(validate_api_token)
) -> DatabaseSession:
    return DatabaseSession()