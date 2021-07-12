import os
import json
import time
from threading import Thread

from flask import (
    Flask,
    request,
    redirect,
    render_template,
    current_app as capp,
)

from rmq_manager import RMQManager


ROOT_DIR = "/workspace/photos"


def new_rmq_connection():
    with open("cfg.json", "r") as f:
        cfg = json.loads(f.read())

    return RMQManager(cfg["user"], cfg["password"], cfg["host"], cfg["port"])


def send(fpath):
    qname = "photo"
    rmq = new_rmq_connection()
    rmq.queue_declare(qname)
    message = json.dumps({"path": fpath})
    rmq.send(qname, message)


def write_to_file(data):
    f = open("result.txt", "w")
    f.write(data)
    f.close()


def update_result(ch, method, properties, body):
    print(f"New body: {body}")
    write_to_file(body.decode())


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY=os.urandom(24))

    @app.route("/")
    def index():
        return redirect("/upload", code=302)

    @app.route("/upload/", methods=("POST", "GET"))
    @app.route("/upload", methods=("POST", "GET"))
    def upload_file():
        result = ""
        if request.method == "POST":
            file = request.files["photo"]
            if not file:
                result = "No image"
            else:
                fpath = os.path.join(ROOT_DIR, file.filename)
                file.save(fpath)
                send(fpath)
                file_empty = True
                while file_empty:
                    with open("result.txt", "r") as f:
                        data = f.read()
                        if data:
                            file_empty = False
                            result = data
                        time.sleep(0.1)

            write_to_file("")

        return render_template("upload.html", result=result)

    return app


qname = "ml_result"
listener = new_rmq_connection()
listener.queue_declare(qname)
t = Thread(
    target=listener.listen,
    args=(
        qname,
        update_result,
    ),
)
t.start()
