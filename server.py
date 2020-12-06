import json
import random
import string

from flask import Flask
from flask import Response
from flask import request
from flask_cors import CORS
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from passlib.hash import sha256_crypt

from event_constraints import EventUserConstraints
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
event_user_constraints = EventUserConstraints(db_filename)


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


@app.route("/event/create", methods=["POST"])
@login_required
def handle_create_event():
    data = request.json
    invite_code = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    event_id = events.add_event(data["name"], data["description"], invite_code)
    event_users.add_event_user(event_id, current_user.get_id(), True)
    return Response(status=200)


@app.route("/event/<event_id>/edit", methods=["POST"])
@login_required
def handle_edit_event(event_id):
    event_user = event_users.get_event_user(event_id, current_user.get_id())
    if event_user is None or not event_user.is_admin:
        return Response(status=403)

    data = request.json
    events.set_name(event_id, data["name"])
    events.set_description(event_id, data["description"])
    return Response(status=200)


@app.route("/event/user-events", methods=["GET"])
@login_required
def handle_user_events():
    data = [event.__dict__ for event in events.get_all_events_for_user(current_user.get_id())]
    return Response(json.dumps(data), status=200)


@app.route("/event/join", methods=["POST"])
@login_required
def handle_join_event():
    invite_code = request.json["invite_code"]
    event = events.get_event_by_invite_code(invite_code)
    if not event:
        return Response(status=404)

    event_users.add_event_user(event.event_id, current_user.get_id())
    return Response(status=200)


@app.route("/event/<event_id>", methods=["GET"])
@login_required
def handle_get_event(event_id):
    event_user = event_users.get_event_user(event_id, current_user.get_id())
    if event_user is None:
        return Response(status=403)

    event = events.get_event_by_id(event_id)
    if event is not None:
        return Response(json.dumps(event.__dict__), status=200)
    else:
        return Response(status=404)


@app.route("/event/<event_id>/users", methods=["GET"])
@login_required
def handle_get_event_users(event_id):
    event_user = event_users.get_event_user(event_id, current_user.get_id())
    if event_user is None:
        return Response(status=403)

    event_users_data = [user.__dict__ for user in event_users.get_event_users(event_id)]
    return Response(json.dumps(event_users_data), status=200)


@app.route("/event/<event_id>/personal-data", methods=["GET"])
@login_required
def handle_get_event_personal_data(event_id):
    event_user = event_users.get_event_user(event_id, current_user.get_id())
    if event_user is None:
        return Response(status=403)

    personal_data = event_users.get_event_user_private_data(event_id, current_user.get_id())
    return Response(json.dumps(personal_data.__dict__), status=200)


@app.route("/event/<event_id>/save-wishes", methods=["POST"])
@login_required
def handle_save_wishes(event_id):
    wishes = request.json["wishes"]
    event_users.set_wishes(event_id, current_user.get_id(), wishes)
    return Response(status=200)


@app.route("/event/<event_id>/constraints", methods=["GET"])
@login_required
def handle_get_event_user_constraints(event_id):
    event_user = event_users.get_event_user(event_id, current_user.get_id())
    if event_user is None:
        return Response(status=403)

    constraints = {}
    for constraint in event_user_constraints.get_user_constraints_for_event(event_id):
        if constraint.user_id not in constraints:
            constraints[constraint.user_id] = []
        constraints[constraint.user_id].append(constraint.__dict__)

    return Response(json.dumps(constraints), status=200)


@app.route("/event/<event_id>/constraints", methods=["POST"])
@login_required
def handle_add_event_user_constraint(event_id):
    event_user = event_users.get_event_user(event_id, current_user.get_id())
    if event_user is None or not event_user.is_admin:
        return Response(status=403)

    data = request.json
    event_user_constraints.add_constraint(event_id, data["user_id"], data["constraint_user_id"])
    return Response(status=200)


@app.route("/event/<event_id>/constraints", methods=["DELETE"])
@login_required
def handle_delete_event_user_constraint(event_id):
    event_user = event_users.get_event_user(event_id, current_user.get_id())
    if event_user is None or not event_user.is_admin:
        return Response(status=403)

    data = request.json
    event_user_constraints.delete_constraint(event_id, data["user_id"], data["constraint_user_id"])
    return Response(status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
