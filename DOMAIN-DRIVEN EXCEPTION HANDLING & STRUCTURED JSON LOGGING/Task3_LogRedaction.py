from loguru import logger
import sys

logger.remove()

logger.add(
    sys.stdout,
    serialize=True
)


def redact(data):
    sensitive_fields = {
        "password",
        "cnic",
        "ssn",
        "token",
        "api_key"
    }

    cleaned = {}

    for key, value in data.items():
        if key.lower() in sensitive_fields:
            cleaned[key] = "******"
        else:
            cleaned[key] = value

    return cleaned


user = {
    "username": "Fahad",
    "password": "abc12345",
    "cnic": "35202-1234567-8",
    "email": "fahad@example.com",
    "token": "XYZ987654321"
}

safe_data = redact(user)

logger.info(
    "User data received",
    **safe_data
)