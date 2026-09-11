from fastapi import FastAPI

app = FastAPI(
    title="Secure API Gateway",
    description="""
# Secure API Gateway

This API demonstrates customized OpenAPI documentation in FastAPI.

## Features

- Rich route descriptions
- Custom response examples
- Organized API tags
- Swagger UI documentation
- ReDoc documentation
""",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "General",
            "description": "General API operations."
        },
        {
            "name": "Administration",
            "description": "Administrative operations and management."
        }
    ]
)


@app.get(
    "/",
    tags=["General"],
    summary="API Health Check",
    description="""
Checks whether the API Gateway is running.

This endpoint can be used to verify that the
API is available and responding to requests.
""",
    response_description="Current API status.",
    responses={
        200: {
            "description": "API is running successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "API Gateway is running"
                    }
                }
            }
        }
    }
)
async def health_check():
    return {
        "status": "success",
        "message": "API Gateway is running"
    }


@app.get(
    "/admin/users",
    tags=["Administration"],
    summary="Get Administrative Users",
    description="""
Retrieves a list of administrative users.

This endpoint is used to view users who have
administrative privileges.
""",
    response_description="List of administrative users.",
    responses={
        200: {
            "description": "Administrative users retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "users": [
                            {
                                "id": 1,
                                "username": "admin",
                                "role": "administrator"
                            },
                            {
                                "id": 2,
                                "username": "manager",
                                "role": "administrator"
                            }
                        ]
                    }
                }
            }
        },
        403: {
            "description": "Access forbidden.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Insufficient permissions"
                    }
                }
            }
        }
    }
)
async def get_admin_users():
    return {
        "users": [
            {
                "id": 1,
                "username": "admin",
                "role": "administrator"
            },
            {
                "id": 2,
                "username": "manager",
                "role": "administrator"
            }
        ]
    }


@app.post(
    "/admin/users",
    tags=["Administration"],
    summary="Create Administrative User",
    description="""
Creates a new administrative user.

The endpoint creates an administrative account
and returns the newly created user information.
""",
    response_description="The newly created administrative user.",
    responses={
        200: {
            "description": "Administrative user created successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User created successfully",
                        "user": {
                            "id": 3,
                            "username": "new_admin",
                            "role": "administrator"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid user information.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid user information"
                    }
                }
            }
        },
        403: {
            "description": "Access forbidden.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Insufficient permissions"
                    }
                }
            }
        }
    }
)
async def create_admin_user():
    return {
        "message": "User created successfully",
        "user": {
            "id": 3,
            "username": "new_admin",
            "role": "administrator"
        }
    }