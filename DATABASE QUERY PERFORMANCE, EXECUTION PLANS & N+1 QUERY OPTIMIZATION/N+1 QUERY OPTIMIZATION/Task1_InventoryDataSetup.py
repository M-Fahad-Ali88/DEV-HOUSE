import os
import random

from django.conf import settings
from django.db import models, connection


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "inventory.db")


if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": DATABASE_PATH,
            }
        },
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    )


import django

django.setup()


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "inventory"


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    class Meta:
        app_label = "inventory"


class InventoryItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory_items"
    )
    quantity = models.IntegerField()

    class Meta:
        app_label = "inventory"


def create_tables():
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Category)
        schema_editor.create_model(Product)
        schema_editor.create_model(InventoryItem)


def create_data():
    print("Creating database tables...")

    create_tables()

    print("Creating categories...")

    categories = []

    for i in range(1, 11):
        category = Category.objects.create(
            name=f"Category {i}"
        )
        categories.append(category)

    print("Creating products...")

    products = []

    for i in range(1, 101):
        product = Product.objects.create(
            name=f"Product {i}",
            category=random.choice(categories)
        )
        products.append(product)

    print("Creating inventory items...")

    for i in range(1, 1001):
        InventoryItem.objects.create(
            product=random.choice(products),
            quantity=random.randint(1, 100)
        )

    print()
    print("===================================")
    print("TASK 1 COMPLETED")
    print("===================================")
    print(f"Categories:       {Category.objects.count()}")
    print(f"Products:         {Product.objects.count()}")
    print(f"Inventory Items:  {InventoryItem.objects.count()}")
    print(f"Database:         {DATABASE_PATH}")


if __name__ == "__main__":
    create_data()