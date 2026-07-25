from pydantic import BaseModel, ValidationError


class Address(BaseModel):
    city: str
    country: str


class User(BaseModel):
    name: str
    age: int
    salary: float
    is_active: bool
    address: Address


test_cases = [
    {
        "name": "Valid Type Coercion",
        "data": {
            "name": "Fahad",
            "age": "22",
            "salary": "75000.50",
            "is_active": "true",
            "address": {
                "city": "Faisalabad",
                "country": "Pakistan"
            }
        }
    },

    {
        "name": "Invalid Integer",
        "data": {
            "name": "Ali",
            "age": "twenty",
            "salary": "50000",
            "is_active": True,
            "address": {
                "city": "Lahore",
                "country": "Pakistan"
            }
        }
    },

    {
        "name": "Missing Nested Field",
        "data": {
            "name": "Ahmed",
            "age": 25,
            "salary": 45000,
            "is_active": True,
            "address": {
                "city": "Karachi"
            }
        }
    },

    {
        "name": "Wrong Boolean Value",
        "data": {
            "name": "Usman",
            "age": 30,
            "salary": 60000,
            "is_active": "maybe",
            "address": {
                "city": "Islamabad",
                "country": "Pakistan"
            }
        }
    }
]


for test in test_cases:

    print(f"\n----- {test['name']} -----")

    try:
        user = User.model_validate(test["data"])
        print("Validation Successful")
        print(user)

    except ValidationError as e:
        print("Validation Failed")
        print(e)