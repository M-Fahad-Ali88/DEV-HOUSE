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

from Task1_InventoryDataSetup import (
    InventoryItem,
    Product,
    Category
)


def test_select_related():
    reset_queries()

    items = list(
        InventoryItem.objects.select_related(
            "product__category"
        )
    )

    for item in items:
        category_name = item.product.category.name

    query_count = len(connection.queries)

    print("===================================")
    print("SELECT_RELATED")
    print("===================================")
    print(f"Inventory Items: {len(items)}")
    print(f"Database Queries: {query_count}")
    print()


def test_prefetch_related():
    reset_queries()

    items = list(
        InventoryItem.objects.prefetch_related(
            "product__category"
        )
    )

    for item in items:
        category_name = item.product.category.name

    query_count = len(connection.queries)

    print("===================================")
    print("PREFETCH_RELATED")
    print("===================================")
    print(f"Inventory Items: {len(items)}")
    print(f"Database Queries: {query_count}")
    print()


if __name__ == "__main__":
    test_select_related()
    test_prefetch_related()