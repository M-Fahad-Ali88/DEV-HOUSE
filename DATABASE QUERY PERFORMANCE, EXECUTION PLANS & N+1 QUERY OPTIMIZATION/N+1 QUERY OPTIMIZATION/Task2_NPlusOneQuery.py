import os

from django.conf import settings
from django.db import connection, reset_queries


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "inventory.db")


if not settings.configured:
    settings.configure(
        DEBUG=True,
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

from Task1_InventoryDataSetup import InventoryItem


def run_n_plus_one():
    reset_queries()

    items = list(
        InventoryItem.objects.all()
    )

    print(f"Inventory Items Retrieved: {len(items)}")
    print()

    for item in items:
        category_name = item.product.category.name

    query_count = len(connection.queries)

    print("===================================")
    print("TASK 2 — N+1 QUERY PROBLEM")
    print("===================================")
    print(f"Inventory Items: {len(items)}")
    print(f"Database Queries: {query_count}")
    print()
    print("Expected Pattern:")
    print("1 query  → Retrieve all inventory items")
    print("1000 queries → Retrieve products")
    print("1000 queries → Retrieve categories")
    print("-----------------------------------")
    print("Expected Total: 2001 queries")


if __name__ == "__main__":
    run_n_plus_one()