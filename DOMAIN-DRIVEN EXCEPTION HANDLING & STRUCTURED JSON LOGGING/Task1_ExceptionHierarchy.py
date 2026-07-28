class IngestionEngineError(Exception):
    """Base exception for the ingestion engine."""
    pass


class InvalidUserDataError(IngestionEngineError):
    """Raised when user data is invalid."""
    pass


class NetworkBoundaryError(IngestionEngineError):
    """Raised when a network error occurs."""
    pass


class DatabaseWriteError(IngestionEngineError):
    """Raised when database write fails."""
    pass


def validate_user(user):
    if not user.get("name"):
        raise InvalidUserDataError("User name is missing.")

    if user.get("network") == "offline":
        raise NetworkBoundaryError("Network is unavailable.")

    if user.get("database") == "down":
        raise DatabaseWriteError("Cannot write to database.")

    print("User processed successfully.")


user = {
    "name": "Fahad",
    "network": "online",
    "database": "up"
}

try:
    validate_user(user)

except IngestionEngineError as error:
    print(f"Application Error: {error}")