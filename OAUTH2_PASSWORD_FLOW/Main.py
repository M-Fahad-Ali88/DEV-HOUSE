from fastapi import FastAPI, Depends, Security, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "admin:read": "Read administrative resources",
        "admin:write": "Modify administrative resources",
    },
)

tokens = {
    "my-secret-token": {
        "username": "fahad",
        "scopes": ["admin:read", "admin:write"],
    },
    "read-only-token": {
        "username": "fahad",
        "scopes": ["admin:read"],
    },
}


@app.post("/token")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    if form_data.username != "fahad" or form_data.password != "12345":
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if "admin:write" in form_data.scopes:
        return {
            "access_token": "my-secret-token",
            "token_type": "bearer",
        }

    return {
        "access_token": "read-only-token",
        "token_type": "bearer",
    }


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user = tokens.get(token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    return user


def check_scope(
    required_scope: str,
    user: dict,
):
    if required_scope not in user["scopes"]:
        raise HTTPException(
            status_code=403,
            detail=f"Missing required scope: {required_scope}",
        )

    return user


@app.get("/admin/users")
def get_admin_users(
    user: Annotated[
        dict,
        Security(get_current_user, scopes=["admin:read"])
    ]
):
    check_scope("admin:read", user)

    return {
        "message": "Admin users retrieved successfully",
        "user": user["username"],
    }


@app.post("/admin/users")
def create_admin_user(
    user: Annotated[
        dict,
        Security(get_current_user, scopes=["admin:write"])
    ]
):
    check_scope("admin:write", user)

    return {
        "message": "Admin user created successfully",
        "user": user["username"],
    }