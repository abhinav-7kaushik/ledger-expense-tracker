# Ledger — Personal Expense Tracker

Full-stack expense tracker built with Flask, SQLAlchemy, and Chart.js. Users sign up, log expenses by category, and view spending on a dashboard with live charts.

## Features
- Signup/login with hashed passwords (Flask-Login + Werkzeug)
- Add, edit, delete expenses (scoped per user)
- Dashboard: total spend, this-month spend, top category, transaction count
- Category breakdown (donut) and 6-month trend (bar) charts via Chart.js
- Filterable expense ledger with running total

## Tech stack
Flask · Flask-SQLAlchemy · Flask-Login · SQLite · Jinja2 · Chart.js

## Run locally
```bash
python3 -m venv venv
pip install -r requirements.txt
python main.py
```
Visit `http://127.0.0.1:5000`, sign up, and start logging expenses. `instance/expenses.db` is created automatically on first run.

## Deployment notes
- Set a real `SECRET_KEY` env variable (the default is dev-only)
- Swap SQLite for Postgres if deploying somewhere like Render/Railway
- Turn off `debug=True` in production
