"""
routes/auth.py - registration, login, logout
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from database.init_db import get_connection

auth_bp = Blueprint("auth", __name__)


class User(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.name = row["name"]
        self.phone = row["phone"]
        self.email = row["email"]
        self.state = row["state"]
        self.district = row["district"]


def load_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return User(row) if row else None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    action = request.form.get("action", "login")
    conn = get_connection()

    if action == "register":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        state = request.form.get("state", "")
        district = request.form.get("district", "")

        if not name or not password or not (phone or email):
            flash("Please fill in your name, password, and at least phone or email.", "error")
            conn.close()
            return redirect(url_for("auth.login"))

        existing = conn.execute(
            "SELECT id FROM users WHERE (phone = ? AND phone != '') OR (email = ? AND email != '')",
            (phone, email),
        ).fetchone()
        if existing:
            flash("An account with that phone or email already exists. Please log in.", "error")
            conn.close()
            return redirect(url_for("auth.login"))

        password_hash = generate_password_hash(password)
        cur = conn.execute(
            "INSERT INTO users (name, phone, email, password_hash, state, district) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, phone or None, email or None, password_hash, state, district),
        )
        conn.commit()
        user_row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
        conn.close()
        login_user(User(user_row))
        return redirect(url_for("main.home"))

    else:  # login
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")
        row = conn.execute(
            "SELECT * FROM users WHERE email = ? OR phone = ?", (identifier, identifier)
        ).fetchone()
        conn.close()

        if row and check_password_hash(row["password_hash"], password):
            login_user(User(row))
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.home"))

        flash("Invalid credentials. Please try again.", "error")
        return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("main.landing"))
