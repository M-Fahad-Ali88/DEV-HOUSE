from pydantic import BaseModel, Field, ValidationError


class Product(BaseModel):
    title: str = Field(min_length=1)
    price: float = Field(gt=0)
    availability: str = Field(min_length=1)


def validate_item(raw_data: dict) -> Product | None:
    try:
        product = Product.model_validate(raw_data)

        print("Valid item:")
        print(product)

        return product

    except ValidationError as error:
        print("Invalid item:")
        print(error)

        return None


def main() -> None:
    raw_data = {
        "title": "A Light in the Attic",
        "price": 51.77,
        "availability": "In stock",
    }

    product = validate_item(raw_data)

    if product:
        print("Item is ready for persistence.")


if __name__ == "__main__":
    main()