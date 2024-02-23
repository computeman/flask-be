from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model, SerializerMixin):
    serialize_rules = ("-_password_hash",)  # Exclude password_hash from serialization

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    postal_code = db.Column(db.Integer, nullable=False)
    aboutme = db.Column(db.String, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __repl__(self):
        return f"user{self.username} , id{self.id}"

    @hybrid_property
    def password_hash(self):
        return self.password

    @password_hash.setter
    def password_hash(self, password):
        # utf-8 encoding and decoding is required in python 3
        password_hash = bcrypt.generate_password_hash(password.encode("utf-8"))
        self.password = password_hash.decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self.password, password.encode("utf-8"))


class Event(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    title = db.Column(db.String(128))
    date = db.Column(db.DateTime)
    time = db.Column(db.Time)
    image = db.Column(db.String(128))
    location = db.Column(db.String(128))
    description = db.Column(db.Text)
    category = db.Column(db.String(64))


class Task(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    assigned_to = db.Column(db.Integer, db.ForeignKey("user.id"))
    title = db.Column(db.String(128))
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    priority = db.Column(db.String(64))
    status = db.Column(db.String(64))
    dependency = db.Column(db.Text)


class EventResource(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    name = db.Column(db.String(128))
    type = db.Column(db.String(64))
    availability = db.Column(db.Boolean)
    reservation_date = db.Column(db.DateTime)


class Budget(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    allocated_budget = db.Column(db.Numeric(10, 2))
    # spent_amount = db.Column(db.Numeric(10, 2))


class Expense(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey("budget.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    name = db.Column(db.Text)
    amount = db.Column(db.Numeric(10, 2))
    date = db.Column(db.DateTime)


class Participant(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    status = db.Column(db.String(64))
    role = db.Column(db.String(64))
