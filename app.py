from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key used for login sessions
app.secret_key = "tarangini-studio-secret-key"


# =========================================================
# DATABASE
# =========================================================

DATABASE = "tarangini.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():

    connection = get_db_connection()

    # =====================================================
    # USERS TABLE
    # =====================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)


    # =====================================================
    # LESSON PROGRESS TABLE
    # =====================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS lessons_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            lesson_name TEXT NOT NULL,

            completed INTEGER DEFAULT 0,

            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)


    # =====================================================
    # RIYAZ SESSIONS TABLE
    # =====================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS riyaz_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            practice_date DATE NOT NULL,

            duration_minutes INTEGER NOT NULL,

            topic TEXT,

            notes TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)


    # =====================================================
    # ACHIEVEMENTS TABLE
    # =====================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            achievement_name TEXT NOT NULL,

            achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)


    connection.commit()

    connection.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# LEARN
# =========================================================

@app.route("/learn")
def learn():
    return render_template("learn.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/progress")
def progress():
    return render_template("progress.html")


@app.route("/learn/introduction")
def introduction():
    return render_template("lesson-introduction.html")


@app.route("/learn/history")
def history():
    return render_template("lesson-history.html")


@app.route("/learn/gharanas")
def gharanas():
    return render_template("lesson-gharanas.html")


@app.route("/learn/terminology")
def terminology():
    return render_template("lesson-terminology.html")


@app.route("/learn/tatkar")
def tatkar():
    return render_template("lesson-tatkar.html")


@app.route("/learn/hastak")
def hastak():
    return render_template("lesson-hastak.html")

@app.route("/learn/chakkar")
def chakkar():
    return render_template("lesson-chakkar.html")


# =========================================================
# SIGNUP
# =========================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check empty fields
        if not name or not email or not password:
            return render_template(
                "signup.html",
                error="Please fill in all fields."
            )

        # Check password confirmation
        if password != confirm_password:
            return render_template(
                "signup.html",
                error="Passwords do not match."
            )

        # Check password length
        if len(password) < 6:
            return render_template(
                "signup.html",
                error="Password must contain at least 6 characters."
            )

        connection = get_db_connection()

        # Check whether email already exists
        existing_user = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            connection.close()

            return render_template(
                "signup.html",
                error="An account with this email already exists."
            )

        # Hash password before storing
        hashed_password = generate_password_hash(password)

        connection.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
            """,
            (name, email, hashed_password)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("login"))

    return render_template("signup.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        connection = get_db_connection()

        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]

            return redirect(url_for("account"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# =========================================================
# ACCOUNT
# =========================================================

@app.route("/account")
def account():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "account.html",
        name=session["user_name"],
        email=session["user_email"]
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    init_database()

    app.run(debug=True)