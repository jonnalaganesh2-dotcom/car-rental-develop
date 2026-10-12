import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Car {self.name}>'

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    days = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    kilometers = db.Column(db.Integer, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    receipt_number = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    car = db.relationship('Car', backref=db.backref('bookings', lazy=True))

    def __repr__(self):
        return f'<Booking {self.user.username} - {self.car.name} - Paid: {self.is_paid} - Receipt: {self.receipt_number}>'
