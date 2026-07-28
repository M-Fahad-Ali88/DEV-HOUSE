import pytest

from app.validator import validate_user


@pytest.mark.parametrize(
    "payload,expected",
    [

        (
            {
                "name": "Ali",
                "age": 25,
                "email": "ali@gmail.com"
            },
            True
        ),

        (
            {
                "name": "",
                "age": 25,
                "email": "ali@gmail.com"
            },
            False
        ),

        (
            {
                "name": "Ali",
                "age": 10,
                "email": "ali@gmail.com"
            },
            False
        ),

        (
            {
                "name": "Ali",
                "age": 25,
                "email": "aligmail.com"
            },
            False
        ),

        (
            {
                "name": 123,
                "age": 25,
                "email": "ali@gmail.com"
            },
            False
        ),

        (
            {
                "age": 25,
                "email": "ali@gmail.com"
            },
            False
        ),

        (
            {},
            False
        ),

        (
            None,
            False
        ),

        (
            [],
            False
        ),

        (
            "Hello",
            False
        ),
    ]
)

def test_validate_user(payload, expected):
    assert validate_user(payload) == expected