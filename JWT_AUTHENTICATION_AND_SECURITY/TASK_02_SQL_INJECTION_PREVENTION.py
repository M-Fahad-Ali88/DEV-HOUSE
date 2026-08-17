from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sql_security.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(30), nullable=False)


def seed_database():
    if User.query.count() == 0:
        users = [
            User(username="admin", role="admin"),
            User(username="fahad", role="user"),
            User(username="normaluser", role="user")
        ]

        db.session.add_all(users)
        db.session.commit()


@app.route("/safe-user-search", methods=["GET"])
def safe_user_search():
    username = request.args.get("username", "")

    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({
            "message": "User not found",
            "input": username,
            "sql_injection_prevented": True
        }), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "sql_injection_prevented": True
    }), 200


@app.route("/security-test", methods=["POST"])
def security_test():
    data = request.get_json() or {}

    username = data.get("username", "")

    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({
            "message": "Malicious input was treated as normal data",
            "input": username,
            "protected": True
        }), 200

    return jsonify({
        "message": "Normal user input",
        "username": user.username,
        "role": user.role,
        "protected": True
    }), 200


@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()

    return jsonify([
        {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
        for user in users
    ]), 200


with app.app_context():
    db.create_all()
    seed_database()


if __name__ == "__main__":
    app.run(port=5001, debug=True)