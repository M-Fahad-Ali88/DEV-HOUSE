from loguru import logger
import sys

logger.remove()

logger.add(
    sys.stdout,
    serialize=True,
    level="INFO"
)

logger.info(
    "User login successful",
    user="Fahad",
    module="Authentication",
    request_id="REQ-1001"
)

logger.warning(
    "Slow API response",
    endpoint="/login",
    response_time=2.8
)

logger.error(
    "Database connection failed",
    database="UsersDB"
)