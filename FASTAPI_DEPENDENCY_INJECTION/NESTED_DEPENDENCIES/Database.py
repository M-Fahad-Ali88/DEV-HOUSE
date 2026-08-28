class DatabaseSession:
    def __init__(self):
        self.connected = True

    def get_user(self, user_id: int):
        return {
            "id": user_id,
            "name": "Fahad"
        }

    def close(self):
        self.connected = False