from flask import Flask
from flask import Response
from flask import request
from flask_cors import CORS

server = Flask(__name__)
cors = CORS(server)


@server.route("/ping", methods=["GET"])
def handle_ping():
    return Response("Pong", status=200)


@server.route("/registration", methods=["POST"])
def handle_registration():
    print("Registration")
    print(request.form)
    return Response("Pong", status=200)


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=3000)
