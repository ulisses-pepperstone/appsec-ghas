#!/usr/bin/env python

import hashlib
import http
import os
import peewee
import uuid

from flask import Flask, request

# Database setup
db = peewee.SqliteDatabase("appsec.sqlite")

# Database models
class User(peewee.Model):
    id = peewee.UUIDField(primary_key=True)
    email = peewee.CharField(unique=True)
    password_hash = peewee.CharField(unique=True)
    class Meta:
        database = db

# Flask setup
app = Flask(__name__)


@app.route("/", methods=["GET"])
def root():
    return {"status": "ok"}

@app.route("/register", methods=["POST"])
def register():
    try:
        payload = request.get_json()
        if "email" in payload and "password" in payload:
            password_hash = hashlib.pbkdf2_hmac(
                hash_name="sha256",
                password=payload["password"].encode("utf-8"),
                salt=payload["email"].encode("utf-8"),
                iterations=1_000_000,
            )
            user = User.create(
                id=uuid.uuid4(),
                email=payload["email"],
                password_hash=password_hash.hex()
            )
            return { "status": "ok", "user_id": user.get_id()}, http.HTTPStatus.OK
        return { "status": "error", "reason": "invalid registration request" }, http.HTTPStatus.BAD_REQUEST
    except Exception as err:
        return {"status":"error", "reason": str(err)}, http.HTTPStatus.BAD_REQUEST

@app.route("/auth", methods=["POST"])
def authenticate():
    try:
        payload = request.get_json()
        if "email" in payload and "password" in payload:
            password_hash = hashlib.pbkdf2_hmac(
                hash_name="sha256",
                password=payload["password"].encode("utf-8"),
                salt=payload["email"].encode("utf-8"),
                iterations=1_000_000,
            )
            user = User.select().where(
                (User.email == payload["email"]) &
                (User.password_hash == password_hash.hex())
            ).get()
            return { "status": "ok", "user_id": user.get_id()}, http.HTTPStatus.OK
        return { "status": "error", "reason": "invalid registration request" }, http.HTTPStatus.UNAUTHORIZED
    except Exception as err:
        return {"status":"error", "reason": str(err)}, http.HTTPStatus.UNAUTHORIZED


@app.route("/upload/<filename>", methods=["POST", "PUT"])
def upload(filename: str):
    try:
        user_id = request.headers.get("x-user-id")
        if user_id is None:
            return {"status":"error", "reason": "user id required"}, http.HTTPStatus.UNAUTHORIZED
        user = User.select().where(User.id == user_id).get()
        output_path = os.path.join(os.path.dirname(__file__), user.email, filename)
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(name=os.path.dirname(output_path), mode=0o777)
        data = request.get_data()
        with open(output_path, "wb") as file_io:
            file_io.write(data)
        return {"status": "ok", "path": output_path}
    except Exception as err:
        return {"status":"error", "reason": str(err)}, http.HTTPStatus.UNAUTHORIZED


if __name__ == "__main__":
    db.connect()
    db.create_tables([User])

    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode)
