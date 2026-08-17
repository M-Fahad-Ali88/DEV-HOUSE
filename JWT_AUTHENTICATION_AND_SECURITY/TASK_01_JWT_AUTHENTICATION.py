from datetime import timedelta

from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///security.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config[
    "JWT_SECRET_KEY"
] = "a7f9K2mP8xQ4vN6zR1tY5wC3sE8uL0pA"

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

db = SQLAlchemy(app)
jwt = JWTManager(app)


# =========================
# JWT ERROR HANDLERS
# =========================

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({
        "msg": error
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "msg": error
    }), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "msg": "Token has expired"
    }), 401


# =========================
# DATABASE MODELS
# =========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(30),
        nullable=False,
        default="user"
    )


class Ledger(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    description = db.Column(
        db.String(200),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )


# =========================
# PERMISSION DECORATOR
# =========================

def permission_required(required_role):

    def decorator(function):

        def wrapper(*args, **kwargs):

            claims = get_jwt()

            user_role = claims.get("role")

            if user_role != required_role:
                return jsonify({
                    "error": "Forbidden",
                    "message": "Insufficient permissions"
                }), 403

            return function(*args, **kwargs)

        wrapper.__name__ = function.__name__

        return wrapper

    return decorator


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json() or {}

    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")

    if not username or not password:
        return jsonify({
            "error": "Username and password are required"
        }), 400

    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:
        return jsonify({
            "error": "Username already exists"
        }), 409

    password_hash = generate_password_hash(
        password
    )

    user = User(
        username=username,
        password_hash=password_hash,
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully"
    }), 201


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json() or {}

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(
        username=username
    ).first()

    if user is None:

        return jsonify({
            "error": "Invalid username or password"
        }), 401

    if not check_password_hash(
        user.password_hash,
        password
    ):

        return jsonify({
            "error": "Invalid username or password"
        }), 401

    additional_claims = {
        "role": user.role
    }

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims
    )

    refresh_token = create_refresh_token(
        identity=str(user.id)
    )

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }), 200


# =========================
# REFRESH TOKEN
# =========================

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    user_id = get_jwt_identity()

    user = db.session.get(
        User,
        int(user_id)
    )

    if user is None:

        return jsonify({
            "error": "User not found"
        }), 404

    additional_claims = {
        "role": user.role
    }

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims
    )

    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer"
    }), 200


# =========================
# PROFILE
# =========================

@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    user_id = get_jwt_identity()

    user = db.session.get(
        User,
        int(user_id)
    )

    if user is None:

        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role
    }), 200


# =========================
# GET LEDGER
# =========================

@app.route("/ledger", methods=["GET"])
@jwt_required()
def get_ledger():

    entries = Ledger.query.all()

    return jsonify([
        {
            "id": entry.id,
            "description": entry.description,
            "amount": entry.amount
        }
        for entry in entries
    ]), 200


# =========================
# CREATE LEDGER
# ADMIN ONLY
# =========================

@app.route("/ledger", methods=["POST"])
@jwt_required()
@permission_required("admin")
def create_ledger():

    data = request.get_json() or {}

    description = data.get("description")
    amount = data.get("amount")

    if description is None or amount is None:

        return jsonify({
            "error": "Description and amount are required"
        }), 400

    try:
        amount = float(amount)

    except (TypeError, ValueError):

        return jsonify({
            "error": "Amount must be a number"
        }), 400

    entry = Ledger(
        description=description,
        amount=amount
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({
        "message": "Ledger entry created",
        "id": entry.id
    }), 201


# =========================
# DELETE LEDGER
# ADMIN ONLY
# =========================

@app.route(
    "/ledger/<int:ledger_id>",
    methods=["DELETE"]
)
@jwt_required()
@permission_required("admin")
def delete_ledger(ledger_id):

    entry = db.session.get(
        Ledger,
        ledger_id
    )

    if entry is None:

        return jsonify({
            "error": "Ledger entry not found"
        }), 404

    db.session.delete(entry)
    db.session.commit()

    return jsonify({
        "message": "Ledger entry deleted"
    }), 200


# =========================
# DATABASE INITIALIZATION
# =========================

with app.app_context():

    db.create_all()


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )