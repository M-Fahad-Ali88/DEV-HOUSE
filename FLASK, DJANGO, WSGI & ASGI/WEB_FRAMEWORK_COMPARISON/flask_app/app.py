from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return jsonify({
        "message": "Hello World",
        "framework": "Flask"
    })


@app.get("/api/users")
def get_users():
    return jsonify([
        {"id": 1, "name": "Ali"},
        {"id": 2, "name": "Ahmed"}
    ])


@app.post("/api/users")
def create_user():
    data = request.get_json()

    return jsonify({
        "message": "User created successfully",
        "user": data
    }), 201


if __name__ == "__main__":
    app.run(debug=True)