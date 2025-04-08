#!/usr/bin/env python

from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return {"status": "ok"}

@app.route("/auth", methods=["POST"])
def authenticate():
    payload = request.get_json()
    if "username" in payload and "password" in payload:
        if payload["username"] == "john.doe@domain.com":
            if payload["password"] == "secret":
                return {"status": "ok"}
            else:
                return {"status": "error", "message": "invalid password"}
        else:
            return {"status": "error", "message": "invalid username"}
    return {"status": "error", "message": "invalid authentication request"}

@app.route("/cart", methods=["GET"])
def cart():
    user = request.headers.get("x-user")
    return {"user": user, "cart": []}

@app.route("/upload/<filename>", methods=["POST","PUT"])
def upload(filename: str):
    output_path = os.path.join(os.path.dirname(__file__), filename)
    f = request.files["the_file"]
    f.save(output_path)
    return {"status": "ok", "path": output_path}

if __name__ == "__main__":
    import os
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode)
