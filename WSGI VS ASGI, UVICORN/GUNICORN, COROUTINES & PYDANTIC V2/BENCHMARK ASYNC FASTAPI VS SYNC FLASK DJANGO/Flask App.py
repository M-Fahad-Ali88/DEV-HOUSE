import time
import threading

from flask import Flask

app = Flask(__name__)


@app.route("/sync")
def sync_endpoint():
    time.sleep(1)

    return {
        "framework": "Flask",
        "type": "synchronous",
        "thread": threading.current_thread().name
    }


if __name__ == "__main__":
    app.run(port=5000)