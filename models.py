from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TIMESTAMP
import uuid

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    pfpic = db.Column(db.String, nullable=True)
    hashpw = db.Column(db.String, nullable=False)

    def __repr__(self) -> str:
        return f'<User {self.user_id}, {self.user_name}, {self.user_email}>'

# Expense model


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Expense('{self.name}', '{self.amount}')"



class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    # example of an additional field
    interest_rate = db.Column(db.Float, nullable=False)
    # duration of the loan in months
    term_months = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Loan('{self.amount}', '{self.interest_rate}', '{self.term_months}')"
