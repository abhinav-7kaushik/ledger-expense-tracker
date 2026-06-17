import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Central app configuration. Override SECRET_KEY via env var in production."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this-before-deploying")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "instance", "expenses.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
