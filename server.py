import json
import random
import string

from flask import Flask
from flask import Response
from flask import request
from flask_cors import CORS
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from passlib.hash import sha256_crypt

from event_users import EventUsers
from events import Events
from users import Users

app = Flask(__name__)
app.secret_key = 'lgnqgblksgnsgnleng'

cors = CORS(app, supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)

db_filename = "./secret_santa.sqlite"

users = Users(db_filename)
events = Events(db_filename)
event_users = EventUsers(db_filename)


@login_manager.user_loader
def load_user(user_id):
    return users.get_user_by_id(user_id)


@app.route("/ping", methods=["GET", "POST"])
def handle_ping():
    return Response("Pong", status=200)


@app.route("/registration", methods=["POST"])
def handle_registration():
    email = request.form["email"]
    name = email.split("@")[0]
    password = request.form["password"]
    password_hash = sha256_crypt.hash(password)
    user_id = users.add_user(email, name, password_hash)
    user = users.get_user_by_id(user_id)
    login_user(user, remember=True)
    return Response(status=200)


@app.route("/login", methods=["POST"])
def handle_login():
    if current_user.is_authenticated:
        return Response(status=200)

    email = request.form["email"]
    password = request.form["password"]
    password_hash = users.get_password_hash_by_email(email)
    if password_hash and sha256_crypt.verify(password, password_hash):
        user = users.get_user_by_email(email)
        login_user(user, remember=True)
        return Response(status=200)

    return Response("Wrong user or password", status=401)


@app.route("/logout", methods=["POST"])
@login_required
def handle_logout():
    logout_user()
    return Response(status=200)


@app.route("/current-user", methods=["GET"])
def handle_current_user():
    if current_user.is_authenticated:
        return Response(json.dumps(current_user.__dict__), status=200)
    return Response(status=200)


@app.route("/save-profile", methods=["POST"])
@login_required
def handle_save_profile():
    data = request.json
    if "name" in data:
        users.set_name(current_user.get_id(), data["name"])
    return Response(status=200)


@app.route("/create-event", methods=["POST"])
@login_required
def handle_create_event():
    data = request.json
    invite_code = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    event_id = events.add_event(data["name"], data["description"], invite_code)
    event_users.add_event_user(event_id, current_user.get_id(), True)
    return Response(status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
