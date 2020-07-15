from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Integer, String, DateTime, Column
import datetime


def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["TESTING"] = True
    db.app = app
    db.init_app(app)
    db.create_all()


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(256))
    password = Column(String(256))
    active = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "email": self.email,
            "password": self.password,
            "active": self.active,
            "created_date": self.created_date.strftime("%Y-%m-%d %H:%M:%S"),
        }


class Todo(db.Model):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True)
    category = Column(String(256))
    done = Column(Boolean, default=False)
    user_id = Column(Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", backref=db.backref("users"))

    def __init__(self, category, done, user_id):
        self.category = category
        self.done = done
        self.user_id = user_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "category": self.category,
            "done": self.done,
            "user_id": self.user_id,
        }

