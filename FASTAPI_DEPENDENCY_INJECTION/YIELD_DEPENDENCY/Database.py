class DatabaseSession:
    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True
        print("Database connected")

    def close(self):
        self.connected = False
        print("Database connection closed")

    def get_users(self):
        return [
            {"id": 1, "name": "Fahad"},
            {"id": 2, "name": "Ali"}
        ]