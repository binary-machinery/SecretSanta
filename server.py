from flask import Flask
from flask import Response
from flask import request
from flask_cors import CORS

from passlib.hash import sha256_crypt

from users import Users

server = Flask(__name__)
cors = CORS(server)

db_filename = "./secret_santa.sqlite"

users = Users(db_filename)


@server.route("/ping", methods=["GET"])
def handle_ping():
    return Response("Pong", status=200)


@server.route("/registration", methods=["POST"])
def handle_registration():
    email = request.form["email"]
    password = request.form["password"]
    password_hash = sha256_crypt.hash(password)
    users.add_user(email, password_hash)
    return Response(status=200)


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=3000)
