from flask import Flask, request
from flask_restx import Resource, Api, fields
from flask_sqlalchemy import SQLAlchemy
from models import setup_db, User, Todo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)
from flask_cors import CORS, cross_origin
import re
import os
import smtplib
import imghdr
from email.message import EmailMessage
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature, SignatureExpired

app = Flask(__name__)
app.secret_key = "markus"
setup_db(app, database_path="postgresql://markus:test@134.122.78.140:5432/register")
jwt = JWTManager(app)
db = SQLAlchemy(app)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app, version="1.0", title="TodoMVC API", description="A simple TodoMVC API",)
bcrypt = Bcrypt()

s = URLSafeTimedSerializer(app.secret_key)

ns = api.namespace("todos", description="TODO operations")

# https://stackoverflow.com/questions/49226806/python-check-for-a-valid-email
def is_valid_email(email):
    if len(email) > 7:
        return bool(
            re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email)
        )


@api.route("/register")
class UserRegister(Resource):
    def post(self):
        """Allows a new user to register with his email and password"""

        error = False
        email = request.get_json()["email"]

        if is_valid_email(email) is False:
            return {"message": "Invalid Email"}, 409

        password = request.get_json()["password"]

        filtereduser = User.query.filter_by(email=email).one_or_none()
        if filtereduser is not None:
            return {"message": "User already exists"}, 401

        try:
            password = bcrypt.generate_password_hash(password).decode("utf8")
            newuser = User(email=email, password=password)
            newuser.insert()
        except:
            error = True
            db.session.rollback()
            return {"error": 404}, 404
        finally:
            db.session.close()
        if error is False:
            return {"success": 200}, 201


@api.route("/login")
class UserLogin(Resource):
    def post(self):
        """Allows a new user to login with his email and password"""

        email = request.get_json()["email"]
        password = request.get_json()["password"]

        user = User.query.filter_by(email=email).one_or_none()

        if user is None:
            return {"message": "user does not exist"}, 404

        user = user.format()
        if bcrypt.check_password_hash(pw_hash=user["password"], password=password):

            if user["active"]:
                access_token = create_access_token(identity=user)
                return (
                    {"access_token": access_token, "message": "Login successful",},
                    200,
                )

            else:
                return {"message": "User not activated"}, 400

        else:
            return {"message": "Wrong credentials"}, 401


@api.route("/confirm")
class Confirm(Resource):
    def post(self):
        email = request.get_json()["email"]

        user = User.query.filter_by(email=email).one_or_none()
        if user is None:
            return {"message": "User not found"}

        token = s.dumps(email, salt="email-confirmation")

        EMAIL_ADDRESS = os.environ.get("MAIL_USERNAME")
        EMAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

        msg = EmailMessage()
        msg["Subject"] = "Confirmation email"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email

        msg.set_content(
            "Please copy this confirmation link into your browser: localhost:5000/confirm/"
            + token
        )

        with smtplib.SMTP_SSL(
            os.environ.get("MAIL_SERVER"), os.environ.get("MAIL_PORT")
        ) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return {"message": "mail sent successful"}


@api.route("/confirm/<token>")
class ConfirmToken(Resource):
    def get(self, token):

        try:
            email = s.loads(token, salt="email-confirmation", max_age=200)
            user = User.query.filter_by(email=email).one_or_none()
            print(user.format())

            if user is None:
                return {"message": "user does not exist"}, 404
            elif user.active:
                return {"message": "user already activated"}, 403
            else:
                user.active = True
                user.update()
                return {"message": "Activation successful"}, 200

        except BadTimeSignature:
            return {"message": "Invalid signature"}, 403
        except SignatureExpired:
            return {"message": "Link expired"}, 404


@api.route("/todos/<int:id>")
class AllTodos(Resource):
    def get(self, id):
        todos = Todos.query.filter_by(user_id=id).all()
        todos = [todo.format() for todo in todos]
        return {"message": todos}, 200

    def post(self, id):
        category = request.get_json()["category"]
        done = request.get_json()["done"]

        try:
            exist_check = User.query.filter_by(id=id).one_or_none()
            if exist_check:
                new_todo = Todo(category=category, done=done, user_id=id)
                new_todo.insert()
                return {"message": "Todo was created"}, 200
            else:
                return {"message": "User not found"}, 404
        except:
            return {"message": "Could not create new todo"}, 404
        finally:
            db.session.close()


@api.route("/delete/<int:id>")
class DeleteUser(Resource):
    def get(self, id):
        User.query.filter_by(id=id).one_or_none().delete()


if __name__ == "__main__":
    app.run(port=5000, debug=True)
