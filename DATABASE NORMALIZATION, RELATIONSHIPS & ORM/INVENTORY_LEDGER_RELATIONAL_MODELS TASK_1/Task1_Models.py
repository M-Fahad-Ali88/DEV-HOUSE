from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


db  = SQLAlchemy()

class Role(db.Model):
    __tablename__ = "roles"

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable = False, unique = True)

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable = False, unique = True)
    email = db.Column(db.String(100), nullable = False, unique = True)

    role_id = db.Column(
        db.Integer, 
        db.ForeignKey("roles.role_id"), 
        nullable = False
    )

class Product(db.Model):
    __tablename__ = "products"

    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable = False, unique = True)
    current_stock = db.Column(db.Integer, nullable = False, default = 0)

class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    movement_id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.product_id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    movement_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    movement_date = db.Column(
        db.DateTime,
        default = lambda: datetime.now(timezone.utc)
    )


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    audit_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    action = db.Column(db.String(255), nullable=False)
    action_date = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
