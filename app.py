import os
from flask import Flask, abort, render_template, redirect, request, send_from_directory, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, DateField
from wtforms.validators import DataRequired
from models import User, Expense, Loan, db
import matplotlib.pyplot as plt
import io
import base64
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://pennyperfect_user:InZBpjqXmDVYAkgyWxEoisf714X84m7M@dpg-coohs6n79t8c73bej6tg-a.ohio-postgres.render.com:5432/pennyperfect'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('APP_SECRET_KEY', 'strawberry')
db.init_app(app)
bcrypt = Bcrypt(app)
# Required callback to load user


def load_user(user_id):
    return User.query.get(int(user_id))


def addRecord(FlaskForm):
    name = StringField('Expense Name')
    cost = FloatField('Expense Amount')
    # updated = HiddenField()
    submit = SubmitField('Add/Update Record')


class ExpenseForm(FlaskForm):
    expense_name = StringField('Expense Name', validators=[DataRequired()])
    expense_amount = FloatField('Expense Amount', validators=[DataRequired()])
    submit = SubmitField('Add Expense')


class LoanForm(FlaskForm):
    loan_name = StringField('Loan Name', validators=[DataRequired()])
    loan_amount = FloatField('Loan Amount', validators=[DataRequired()])
    loan_interest = FloatField('Loan Interest', validators=[DataRequired()])
    loan_repayment = DateField(
        'Loan Repayment Date', validators=[DataRequired()])
    submit = SubmitField('Add Expense')
# Routes


@app.route('/')
def home():
    perform_login = False
    if 'username' in session:
        # Assuming you're using Flask-Login or similar and storing the username in the session
        username = session['username']
        perform_login = True
        return render_template('home.html', current_user=User.query.filter_by(username=username).first(), perform_login=perform_login)
    else:
        return render_template('home.html', perform_login=perform_login)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        raw_password = request.form.get('password')
        if perform_login(username, raw_password):
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid username or password")
    if 'username' in session:
        return redirect('/')
    return render_template('login.html', loggedIn=False)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        hashpw = bcrypt.generate_password_hash(raw_password, 12).decode()
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        if existing_user:
            error = 'Username already exists. Please choose a different one.'
            return render_template('register.html', error=error)
        elif existing_email:
            error = 'Email address already registered. Please use a different one.'
            return render_template('register.html', error=error)
        else:
            new_user = User(username=username, hashpw=hashpw, email=email)
            db.session.add(new_user)
            db.session.commit()
            perform_login(username, raw_password)
            return redirect('/')
    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'username' in session:
        del session['username']
    return redirect('/')


def perform_login(username, raw_password):
    if not username or not raw_password:
        abort(401)
    existing_user = User.query.filter_by(username=username).first()
    if not existing_user or not bcrypt.check_password_hash(existing_user.hashpw, raw_password):
        return False
    session['username'] = username
    return True


@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('budget_calculator'))

@app.route('/delete_loan/<int:loan_id>', methods=['POST'])
def delete_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    db.session.delete(loan)
    db.session.commit()
    return redirect(url_for('loan_calculator'))

@app.route('/set_monthly_income', methods=['POST'])
def set_monthly_income():
    monthly_income = float(request.form['monthly_income'])
    session['monthly_income'] = monthly_income
    return redirect(url_for('budget_calculator'))


@app.route('/set_housing_expenses', methods=['POST'])
def set_housing_expenses():
    housing_expenses = float(request.form['housing_expenses'])
    session['housing_expenses'] = housing_expenses
    return redirect(url_for('budget_calculator'))


@app.route('/loan_calculator', methods=['GET', 'POST'])
def loan_calculator():
    # Get the current user
    username = session['username']
    current_user = User.query.filter_by(username=username).first()
    loans = Loan.query.filter_by(loan_id=current_user.id).all()
    form = LoanForm()
    if request.method == 'POST':
        loan_name = form.loan_name.data
        loan_amount = form.loan_amount.data
        loan_interest = form.loan_interest.data
        loan_repayment = form.loan_repayment.data

        # Create a new loan instance associated with the current user
        new_loan = Loan(
            loan_id=current_user.id,
            name=loan_name,
            amount=loan_amount,
            interest_rate=loan_interest,
            term_months=loan_repayment,
        )
        # Add the new loan to the database session and commit
        db.session.add(new_loan)
        db.session.commit()
        # Redirect to a success page or wherever you want
        return redirect(url_for('loan_calculator'))

    return render_template('loan_calculator.html', form=form, loans=loans)


@app.route('/loan_calendar', methods=['GET', 'POST'])
def loan_calendar():
    # Add your loan calendar logic here
    return render_template('loan_calendar.html')


@app.route('/budget_calculator', methods=['GET', 'POST'])
def budget_calculator():
    form = ExpenseForm()
    username = session['username']
    current_user = User.query.filter_by(username=username).first()
    if request.method == 'POST':
        expense_name = form.expense_name.data
        expense_amount = form.expense_amount.data
        new_expense = Expense(
            name=expense_name, amount=expense_amount, user_id=current_user.id)
        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('budget_calculator'))
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    total_expenses = sum(expense.amount for expense in expenses)
    monthly_income = session.get('monthly_income')
    if monthly_income is not None:
        remaining_budget = monthly_income - total_expenses
        if remaining_budget >= 0:
            budget_status = f"You have ${remaining_budget:,.2f} left over each month."
            budget_status = f"You have ${remaining_budget:,.2f} left over each month."
        else:
            budget_status = f"You are ${abs(remaining_budget):.2f} over budget."
            budget_status = f"You are ${abs(remaining_budget):.2f} over budget."
    else:
        budget_status = "Monthly income not set."

    expense_names = [expense.name for expense in expenses]
    expense_amounts = [expense.amount for expense in expenses]
    plt.figure(figsize=(8, 6))
    plt.pie(expense_amounts, labels=expense_names, autopct='%1.1f%%')
    plt.title('Budget Expenses')
    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    encoded_image = base64.b64encode(image_stream.getvalue()).decode()
    return render_template('budget_calculator.html', form=form, plot_url=encoded_image, total_expenses=total_expenses, budget_status=budget_status, expenses=expenses)

    if __name__ == '__main__':
        app.run(debug=True)
