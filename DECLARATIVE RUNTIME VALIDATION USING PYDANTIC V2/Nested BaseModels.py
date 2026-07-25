from pydantic import BaseModel, EmailStr
from typing import List, Optional


class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str


class EmergencyContact(BaseModel):
    name: str
    relationship: str
    phone: str


class Company(BaseModel):
    company_name: str
    department: str
    employee_id: int


class Preferences(BaseModel):
    newsletter: bool
    notifications: bool
    language: str


class User(BaseModel):
    first_name: str
    last_name: str
    age: int
    email: EmailStr
    phone: str
    address: Address
    company: Company
    emergency_contacts: List[EmergencyContact]
    preferences: Preferences
    hobbies: Optional[List[str]] = None


payload = {
    "first_name": "Fahad",
    "last_name": "Ali",
    "age": 22,
    "email": "fahad@example.com",
    "phone": "03001234567",
    "address": {
        "street": "Main Road",
        "city": "Faisalabad",
        "state": "Punjab",
        "zip_code": "38000",
        "country": "Pakistan"
    },
    "company": {
        "company_name": "ABC Software",
        "department": "Development",
        "employee_id": 101
    },
    "emergency_contacts": [
        {
            "name": "Ahmed",
            "relationship": "Brother",
            "phone": "03111234567"
        },
        {
            "name": "Ali",
            "relationship": "Friend",
            "phone": "03221234567"
        }
    ],
    "preferences": {
        "newsletter": True,
        "notifications": False,
        "language": "English"
    },
    "hobbies": [
        "Gaming",
        "Programming",
        "Cricket"
    ]
}


user = User.model_validate(payload)

print("Validated User Data:")
print(user)

print("\nUser Name:", user.first_name, user.last_name)
print("City:", user.address.city)
print("Company:", user.company.company_name)
print("First Emergency Contact:", user.emergency_contacts[0].name)
print("Hobbies:", user.hobbies)