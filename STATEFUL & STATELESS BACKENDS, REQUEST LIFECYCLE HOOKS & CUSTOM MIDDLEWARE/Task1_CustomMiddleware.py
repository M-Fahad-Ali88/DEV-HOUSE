#This single file will demonstrate:

#Request interception
#Custom header validation
#Execution latency measurement
#Request/response logging

from flask import Flask, request, jsonify
import time

app = Flask(__name__)


@app.before_request
def before_request():
    request.start_time = time.perf_counter()

    api_key = request.headers.get("X-API-KEY")

    if api_key != "abc123":
        return jsonify({"error": "Invalid or missing X-API-KEY"}), 401


@app.after_request
def after_request(response):
    execution_time = time.perf_counter() - request.start_time

    response.headers["X-Execution-Time"] = f"{execution_time:.6f}s"

    print(
        f"{request.method} {request.path} "
        f"| Status: {response.status_code} "
        f"| Execution Time: {execution_time:.6f}s"
    )

    return response


@app.route("/")
def home():
    return jsonify({"message": "Request processed successfully"})


@app.route("/products")
def products():
    return jsonify({
        "products": ["Laptop", "Phone", "Keyboard"]
    })


if __name__ == "__main__":
    app.run(debug=True)