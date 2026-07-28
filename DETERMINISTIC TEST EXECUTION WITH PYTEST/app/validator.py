def validate_user(payload):
    if not isinstance(payload, dict):
        return False

    required = ["name", "age", "email"]

    for field in required:
        if field not in payload:
            return False

    if not isinstance(payload["name"], str):
        return False

    if payload["name"] == "":
        return False

    if not isinstance(payload["age"], int):
        return False

    if payload["age"] < 18:
        return False

    if "@" not in payload["email"]:
        return False

    return True