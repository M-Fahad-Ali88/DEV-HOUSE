from pydantic import BaseModel, EmailStr, field_validator, model_validator


class User(BaseModel):
    first_name: str
    last_name: str
    age: int
    email: EmailStr
    phone: str
    password: str
    confirm_password: str

    @field_validator("first_name", "last_name")
    @classmethod
    def remove_extra_spaces(cls, value: str):
        return value.strip().title()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr):
        return value.lower().strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str):
        value = value.strip()

        if not value.isdigit():
            raise ValueError("Phone number must contain only digits.")

        if len(value) != 11:
            raise ValueError("Phone number must be exactly 11 digits.")

        return value

    @model_validator(mode="after")
    def validate_user(self):

        if self.age < 18:
            raise ValueError("User must be at least 18 years old.")

        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")

        return self


payload = {
    "first_name": "   fahad   ",
    "last_name": "   ali   ",
    "age": 22,
    "email": "  FAHAD@GMAIL.COM  ",
    "phone": "03001234567",
    "password": "Python123",
    "confirm_password": "Python123"
}


try:
    user = User.model_validate(payload)

    print("Validated User Data")
    print(user)

except Exception as e:
    print("Validation Error")
    print(e)