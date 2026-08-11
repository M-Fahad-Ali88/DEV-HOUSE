import sys
from pathlib import Path

from flask import Flask
from sqlalchemy import text, select

# Task 1 ke models wale folder ko Python path mein add karna
task1_folder = (
    Path(__file__).parent.parent
    / "INVENTORY_LEDGER_RELATIONAL_MODELS TASK_1"
)

sys.path.append(str(task1_folder))

from Task1_Models import db, Product


# Flask application
app = Flask(__name__)

# Task 1 ke same database ko use karna
database_path = task1_folder / "instance" / "inventory.db"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{database_path}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


with app.app_context():

    # ==========================================
    # 1. RAW SQL - SELECT ALL PRODUCTS
    # ==========================================

    print("\n========== RAW SQL ==========")

    raw_sql = text("SELECT * FROM products")

    result = db.session.execute(raw_sql)

    for row in result:
        print(row)


    # ==========================================
    # 2. ORM - SELECT ALL PRODUCTS
    # ==========================================

    print("\n========== ORM ==========")

    products = db.session.execute(
        select(Product)
    ).scalars().all()

    for product in products:
        print(
            product.product_id,
            product.product_name,
            product.current_stock
        )


    # ==========================================
    # 3. ORM QUERY
    # ==========================================

    print("\n========== ORM FILTER ==========")

    statement = select(Product).where(
        Product.product_name == "Laptop"
    )

    products = db.session.execute(
        statement
    ).scalars().all()

    for product in products:
        print(
            product.product_id,
            product.product_name,
            product.current_stock
        )


    # ==========================================
    # 4. GENERATED SQL FROM ORM
    # ==========================================

    print("\n========== GENERATED SQL ==========")

    print(
        statement.compile(
            compile_kwargs={"literal_binds": True}
        )
    )


    # ==========================================
    # 5. ORM INSERT
    # ==========================================

    print("\n========== ORM INSERT ==========")

    new_product = Product(
        product_name="Keyboard",
        current_stock=25
    )

    db.session.add(new_product)
    db.session.commit()

    print("Product inserted using ORM.")


    # ==========================================
    # 6. RAW SQL INSERT
    # ==========================================

    print("\n========== RAW SQL INSERT ==========")

    db.session.execute(
        text("""
            INSERT INTO products
            (product_name, current_stock)
            VALUES (:name, :stock)
        """),
        {
            "name": "Mouse",
            "stock": 50
        }
    )

    db.session.commit()

    print("Product inserted using Raw SQL.")


    # ==========================================
    # 7. SHOW ALL PRODUCTS AGAIN
    # ==========================================

    print("\n========== FINAL PRODUCTS ==========")

    products = db.session.execute(
        select(Product)
    ).scalars().all()

    for product in products:
        print(
            f"ID: {product.product_id} | "
            f"Name: {product.product_name} | "
            f"Stock: {product.current_stock}"
        )