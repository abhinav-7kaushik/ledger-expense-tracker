from collections import defaultdict
from datetime import date, datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from config import Config
from models import Expense, User, db

CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills",
    "Entertainment", "Health", "Education", "Other",
]

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "info"
login_manager.init_app(app)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        elif User.query.filter_by(username=username).first():
            flash("That username is already taken.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("That email is already registered.", "danger")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    expenses = (
        Expense.query.filter_by(user_id=current_user.id)
        .order_by(Expense.date.desc())
        .all()
    )

    total = sum(e.amount for e in expenses)

    category_totals = defaultdict(float)
    for e in expenses:
        category_totals[e.category] += e.amount
    top_category = max(category_totals, key=category_totals.get) if category_totals else "—"

    monthly_totals = defaultdict(float)
    for e in expenses:
        monthly_totals[e.date.strftime("%Y-%m")] += e.amount
    sorted_months = sorted(monthly_totals.items())[-6:]

    this_month_key = date.today().strftime("%Y-%m")
    this_month_total = monthly_totals.get(this_month_key, 0.0)

    return render_template(
        "dashboard.html",
        total=total,
        this_month_total=this_month_total,
        expense_count=len(expenses),
        top_category=top_category,
        category_labels=list(category_totals.keys()),
        category_values=list(category_totals.values()),
        month_labels=[m for m, _ in sorted_months],
        month_values=[v for _, v in sorted_months],
        recent=expenses[:6],
    )

@app.route("/expenses")
@login_required
def expenses_list():
    selected_category = request.args.get("category", "")
    query = Expense.query.filter_by(user_id=current_user.id)
    if selected_category:
        query = query.filter_by(category=selected_category)
    expenses = query.order_by(Expense.date.desc()).all()
    total = sum(e.amount for e in expenses)

    return render_template(
        "expenses.html",
        expenses=expenses,
        categories=CATEGORIES,
        selected_category=selected_category,
        total=total,
    )


def _parse_amount(raw):
    try:
        value = float(raw)
        return value if value > 0 else None
    except (TypeError, ValueError):
        return None


def _parse_date(raw):
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return date.today()


@app.route("/expenses/add", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        amount = _parse_amount(request.form.get("amount"))
        category = request.form.get("category")
        description = request.form.get("description", "").strip()
        expense_date = _parse_date(request.form.get("date"))

        if amount is None or category not in CATEGORIES:
            flash("Please provide a valid amount and category.", "danger")
        else:
            db.session.add(
                Expense(
                    amount=amount,
                    category=category,
                    description=description,
                    date=expense_date,
                    user_id=current_user.id,
                )
            )
            db.session.commit()
            flash("Expense added.", "success")
            return redirect(url_for("expenses_list"))

    return render_template(
        "add_expense.html", categories=CATEGORIES, today=date.today().isoformat()
    )


@app.route("/expenses/<int:expense_id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.filter_by(
        id=expense_id, user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":
        amount = _parse_amount(request.form.get("amount"))
        category = request.form.get("category")

        if amount is None or category not in CATEGORIES:
            flash("Please provide a valid amount and category.", "danger")
        else:
            expense.amount = amount
            expense.category = category
            expense.description = request.form.get("description", "").strip()
            expense.date = _parse_date(request.form.get("date"))
            db.session.commit()
            flash("Expense updated.", "success")
            return redirect(url_for("expenses_list"))

    return render_template("edit_expense.html", expense=expense, categories=CATEGORIES)


@app.route("/expenses/<int:expense_id>/delete", methods=["POST"])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.filter_by(
        id=expense_id, user_id=current_user.id
    ).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.", "info")
    return redirect(url_for("expenses_list"))


if __name__ == "__main__":
    app.run(debug=False)