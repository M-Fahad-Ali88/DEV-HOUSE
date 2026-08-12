from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    event
)

from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
    joinedload,
    subqueryload
)


Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    products = relationship(
        "Product",
        back_populates="category"
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    category_id = Column(
        Integer,
        ForeignKey("categories.id")
    )

    category = relationship(
        "Category",
        back_populates="products"
    )

    inventory_items = relationship(
        "InventoryItem",
        back_populates="product"
    )


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    product = relationship(
        "Product",
        back_populates="inventory_items"
    )


engine = create_engine(
    "sqlite:///sqlalchemy_inventory.db"
)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


query_count = 0


def count_queries(
    conn,
    cursor,
    statement,
    parameters,
    context,
    executemany
):
    global query_count
    query_count += 1


event.listen(
    engine,
    "before_cursor_execute",
    count_queries
)


def create_data():
    if session.query(InventoryItem).count() > 0:
        return

    categories = []

    for i in range(1, 11):
        category = Category(
            name=f"Category {i}"
        )
        categories.append(category)

    session.add_all(categories)
    session.flush()

    products = []

    for i in range(1, 101):
        product = Product(
            name=f"Product {i}",
            category=categories[(i - 1) % 10]
        )
        products.append(product)

    session.add_all(products)
    session.flush()

    inventory_items = []

    for i in range(1, 1001):
        item = InventoryItem(
            product=products[(i - 1) % 100],
            quantity=(i % 100) + 1
        )
        inventory_items.append(item)

    session.add_all(inventory_items)
    session.commit()


def test_joinedload():
    global query_count

    query_count = 0

    items = (
        session.query(InventoryItem)
        .options(
            joinedload(
                InventoryItem.product
            ).joinedload(
                Product.category
            )
        )
        .all()
    )

    for item in items:
        category_name = item.product.category.name

    print("===================================")
    print("JOINEDLOAD")
    print("===================================")
    print(f"Inventory Items: {len(items)}")
    print(f"Database Queries: {query_count}")
    print()


def test_subqueryload():
    global query_count

    query_count = 0

    items = (
        session.query(InventoryItem)
        .options(
            subqueryload(
                InventoryItem.product
            ).subqueryload(
                Product.category
            )
        )
        .all()
    )

    for item in items:
        category_name = item.product.category.name

    print("===================================")
    print("SUBQUERYLOAD")
    print("===================================")
    print(f"Inventory Items: {len(items)}")
    print(f"Database Queries: {query_count}")
    print()


if __name__ == "__main__":
    create_data()

    test_joinedload()
    test_subqueryload()

    session.close()