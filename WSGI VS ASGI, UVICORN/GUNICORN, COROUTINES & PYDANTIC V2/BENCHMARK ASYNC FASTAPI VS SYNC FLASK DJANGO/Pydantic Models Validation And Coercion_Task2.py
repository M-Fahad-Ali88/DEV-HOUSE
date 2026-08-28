from pydantic import BaseModel, Field, field_validator


class User(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=50
    )

    age: int = Field(
        gt=0,
        le=100
    )

    email: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value.lower() == "admin":
            raise ValueError("Name cannot be admin")

        return value.title()


user = User(
    name="fahad",
    age="20",
    email="fahad@example.com"
)

print(user)
print(type(user.age))