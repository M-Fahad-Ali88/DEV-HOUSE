from flask import Flask, request, jsonify
import time

app = Flask(__name__)

REQUEST_LIMIT = 5
request_count = {}


@app.before_request
def before_request():
    request.start_time = time.perf_counter()

    api_key = request.headers.get("X-API-KEY")

    if api_key != "abc123":
        return jsonify({"error": "Invalid or missing X-API-KEY"}), 401

    client_ip = request.remote_addr

    request_count[client_ip] = request_count.get(client_ip, 0) + 1

    print("\n--- Incoming Request ---")
    print(f"Method: {request.method}")
    print(f"Path: {request.path}")
    print(f"Client IP: {client_ip}")
    print(f"Request Count: {request_count[client_ip]}")

    if request.is_json:
        print(f"Payload: {request.get_json(silent=True)}")

    if request_count[client_ip] > REQUEST_LIMIT:
        return jsonify({"error": "Rate limit exceeded"}), 429


@app.after_request
def after_request(response):
    execution_time = time.perf_counter() - request.start_time
    client_ip = request.remote_addr

    remaining_requests = max(
        0,
        REQUEST_LIMIT - request_count.get(client_ip, 0)
    )

    response.headers["X-Execution-Time"] = f"{execution_time:.6f}s"
    response.headers["X-RateLimit-Limit"] = str(REQUEST_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(remaining_requests)

    print(f"Status: {response.status_code}")
    print(f"Execution Time: {execution_time:.6f}s")
    print("------------------------")

    return response


@app.route("/")
def home():
    return jsonify({
        "message": "Task 2 middleware is working"
    })


@app.route("/products", methods=["GET"])
def products():
    return jsonify({
        "products": ["Laptop", "Phone", "Keyboard"]
    })


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)

    return jsonify({
        "message": "User received",
        "data": data
    }), 201


if __name__ == "__main__":
    app.run(debug=True)