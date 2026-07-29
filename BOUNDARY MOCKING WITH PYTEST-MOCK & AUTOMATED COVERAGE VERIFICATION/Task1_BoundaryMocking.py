from unittest.mock import Mock
import pytest


# External Database Service
class Database:
    def connect(self):
        return "Connected to Database"

    def get_user(self, user_id):
        return {
            "id": user_id,
            "name": "Fahad"
        }


# Application Service
class UserService:

    def __init__(self, database):
        self.database = database

    def fetch_user(self, user_id):
        self.database.connect()
        return self.database.get_user(user_id)


# Test using pytest-mock
def test_fetch_user(mocker):

    # Create mock database
    mock_db = mocker.Mock()

    # Mock return values
    mock_db.connect.return_value = "Mock Connection"

    mock_db.get_user.return_value = {
        "id": 1,
        "name": "Ali"
    }

    # Inject mock database
    service = UserService(mock_db)

    result = service.fetch_user(1)

    # Assertions
    assert result["name"] == "Ali"

    # Verify methods called
    mock_db.connect.assert_called_once()

    mock_db.get_user.assert_called_once_with(1)


def test_database_failure(mocker):

    mock_db = mocker.Mock()

    # Simulate database error
    mock_db.get_user.side_effect = Exception("Database Error")

    service = UserService(mock_db)

    with pytest.raises(Exception):
        service.fetch_user(1)