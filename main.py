#!/usr/bin/env python

from flask import Flask

app = Flask(__name__)

@app.route("/")
def root():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True)