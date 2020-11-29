import flask
from flask import Flask
from flask import Response
from flask import request
from flask_cors import CORS
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from passlib.hash import sha256_crypt

from users import Users

app = Flask(__name__)
app.secret_key = 'lgnqgblksgnsgnleng'

cors = CORS(app, supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)

db_filename = "./secret_santa.sqlite"

users = Users(db_filename)


@login_manager.user_loader
def load_user(user_id):
    print("load_user: " + str(user_id))
    return users.get_user_by_id(user_id)


@app.route("/ping", methods=["GET", "POST"])
def handle_ping():
    print(current_user)
    return Response("Pong", status=200)


@app.route("/registration", methods=["POST"])
def handle_registration():
    email = request.form["email"]
    password = request.form["password"]
    password_hash = sha256_crypt.hash(password)
    users.add_user(email, password_hash)
    return Response(status=200)


@app.route("/login", methods=["POST"])
def handle_login():
    if current_user.is_authenticated:
        print("Already authenticated: " + str(current_user))
        return flask.redirect("http://localhost:8080/")
    email = request.form["email"]
    password = request.form["password"]
    user = users.get_user_by_email(email)
    if user and sha256_crypt.verify(password, user.password_hash):
        print(login_user(user, remember=True))
        print(current_user)
        return flask.redirect("http://localhost:8080/")
    return Response("Wrong user or password", status=403)


@app.route("/logout", methods=["POST"])
@login_required
def handle_logout():
    print("Logout user: " + str(current_user))
    if current_user.is_authenticated:
        print("User found: " + str(current_user))
        logout_user()
    print("After logout: " + str(current_user))
    return flask.redirect("http://localhost:8080/", 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
