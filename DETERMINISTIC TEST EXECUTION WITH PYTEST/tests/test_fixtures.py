def test_function_fixture(sample_user):
    assert sample_user["name"] == "Ali"


def test_database_fixture(database):
    assert database["status"] == "Connected"


def test_session_fixture(app_config):
    assert app_config["environment"] == "Testing"