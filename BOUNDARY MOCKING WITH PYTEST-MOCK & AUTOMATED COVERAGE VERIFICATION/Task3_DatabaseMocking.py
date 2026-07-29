from unittest.mock import Mock
import pytest


# Real Database Class
class DatabaseConnection:

    def connect(self):
        return True

    def execute_query(self, query):
        return [
            {"id": 1, "name": "Fahad"},
            {"id": 2, "name": "Ali"}
        ]

    def close(self):
        return True


# Application Database Service
class UserRepository:

    def __init__(self, database):
        self.database = database

    def get_users(self):

        self.database.connect()

        users = self.database.execute_query(
            "SELECT * FROM users"
        )

        self.database.close()

        return users


# Test Successful Database Query
def test_get_users_success():

    # Create fake database
    mock_db = Mock()

    # Fake database responses
    mock_db.connect.return_value = True

    mock_db.execute_query.return_value = [
        {
            "id": 1,
            "name": "Fahad"
        }
    ]

    mock_db.close.return_value = True


    repository = UserRepository(mock_db)

    result = repository.get_users()


    assert len(result) == 1
    assert result[0]["name"] == "Fahad"


    # Verify database methods
    mock_db.connect.assert_called_once()

    mock_db.execute_query.assert_called_once_with(
        "SELECT * FROM users"
    )

    mock_db.close.assert_called_once()



# Test Database Failure
def test_database_failure():

    mock_db = Mock()


    # Simulate database error
    mock_db.execute_query.side_effect = Exception(
        "Database Connection Failed"
    )


    repository = UserRepository(mock_db)


    with pytest.raises(Exception):
        repository.get_users()



# Test Empty Database
def test_empty_database():

    mock_db = Mock()


    mock_db.execute_query.return_value = []


    repository = UserRepository(mock_db)


    result = repository.get_users()


    assert result == []