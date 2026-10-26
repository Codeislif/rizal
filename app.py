
import os
import sqlite3
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='/static')
app.secret_key = "replace-with-a-private-secret-key"
DATABASE = os.path.join(BASE_DIR, "rizal.db")

MODULES = [
    {
        "title": "Childhood and Family",
        "year": "1861",
        "content": "Jose Rizal was born on June 19, 1861, in Calamba, Laguna. "
        "His parents were Francisco Mercado and Teodora Alonso. "
        "His family encouraged education, reading, and learning."
    },
    {
        "title": "Education",
        "year": "1870s–1880s",
        "content": "Rizal studied at Ateneo Municipal de Manila and the "
        "University of Santo Tomas. He later continued his studies in Europe, "
        "including medicine and ophthalmology."
    },
    {
        "title": "Travels and Experiences",
        "year": "1882 onward",
        "content": "Rizal traveled to Spain and other parts of Europe. "
        "He met fellow reformists and advocated peaceful reforms, equal rights, "
        "and better treatment of Filipinos."
    },
    {
        "title": "His Famous Novels",
        "year": "1887 and 1891",
        "content": "Noli Me Tangere was published in 1887, followed by "
        "El Filibusterismo in 1891. These novels exposed abuses and social "
        "problems during Spanish colonial rule."
    },
    {
        "title": "Exile and Legacy",
        "year": "1892–1896",
        "content": "Rizal was exiled to Dapitan in 1892. He taught students, "
        "practiced medicine, and served the community. He was executed at "
        "Bagumbayan on December 30, 1896, and is remembered as a national hero."
    }
]

QUESTIONS = [
    {
        "question": "When was Jose Rizal born?",
        "options": ["June 19, 1861", "December 30, 1896",
                    "June 12, 1898", "August 21, 1872"],
        "answer": "June 19, 1861"
    },
    {
        "question": "Where was Rizal born?",
        "options": ["Manila", "Calamba, Laguna",
                    "Dapitan", "Cebu"],
        "answer": "Calamba, Laguna"
    },
    {
        "question": "Who was Rizal's mother?",
        "options": ["Gregoria de Jesus", "Melchora Aquino",
                    "Teodora Alonso", "Gabriela Silang"],
        "answer": "Teodora Alonso"
    },
    {
        "question": "Which novel was published in 1887?",
        "options": ["El Filibusterismo", "Noli Me Tangere",
                    "Florante at Laura", "Mi Ultimo Adios"],
        "answer": "Noli Me Tangere"
    },
    {
        "question": "Where was Rizal exiled?",
        "options": ["Vigan", "Cavite", "Dapitan", "Baguio"],
        "answer": "Dapitan"
    },
    {
        "question": "When was Rizal executed?",
        "options": ["June 19, 1861", "December 30, 1896",
                    "April 9, 1942", "June 12, 1898"],
        "answer": "December 30, 1896"
    }
]


def connect():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def initialize_database():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        admin = db.execute(
            "SELECT id FROM users WHERE username = ?", ("admin",)
        ).fetchone()

        if admin is None:
            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", generate_password_hash("admin123"), "admin")
            )


initialize_database()


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("home"))
        return function(*args, **kwargs)
    return wrapper


@app.route("/")
@login_required
def home():
    return render_template(
        "index.html", page="home", modules=MODULES
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            message = "Please complete all fields."
        elif len(username) > 40:
            message = "Username must be 40 characters or fewer."
        elif len(password) < 6:
            message = "Password must contain at least 6 characters."
        else:
            try:
                with connect() as db:
                    db.execute(
                        "INSERT INTO users (username, password, role) "
                        "VALUES (?, ?, 'user')",
                        (username, generate_password_hash(password))
                    )
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                message = "That username already exists."

    return render_template(
        "index.html", page="register", message=message
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with connect() as db:
            user = db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("home"))

        message = "Incorrect username or password."

    return render_template(
        "index.html", page="login", message=message
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/module/<int:module_id>")
@login_required
def module(module_id):
    if not 0 <= module_id < len(MODULES):
        return redirect(url_for("home"))

    return render_template(
        "index.html", page="module",
        module=MODULES[module_id],
        module_id=module_id,
        modules=MODULES
    )


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    score = None
    review = []

    if request.method == "POST":
        score = 0

        for i, question in enumerate(QUESTIONS):
            selected = request.form.get(f"q{i}", "")
            correct = selected == question["answer"]

            if correct:
                score += 1

            review.append({
                "question": question["question"],
                "selected": selected or "No answer",
                "answer": question["answer"],
                "correct": correct
            })

        with connect() as db:
            db.execute(
                "INSERT INTO records (username, score, total) VALUES (?, ?, ?)",
                (session["username"], score, len(QUESTIONS))
            )

    return render_template(
        "index.html", page="quiz", questions=QUESTIONS,
        score=score, review=review
    )


@app.route("/records")
@login_required
def records():
    with connect() as db:
        if session.get("role") == "admin":
            users = db.execute(
                "SELECT id, username, role FROM users ORDER BY id DESC"
            ).fetchall()
            results = db.execute(
                "SELECT * FROM records ORDER BY date DESC, id DESC"
            ).fetchall()
        else:
            users = []
            results = db.execute(
                "SELECT * FROM records WHERE username = ? "
                "ORDER BY date DESC, id DESC",
                (session["username"],)
            ).fetchall()

    return render_template(
        "index.html", page="records",
        users=users, results=results
    )


@app.route("/delete-user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    with connect() as db:
        user = db.execute(
            "SELECT username, role FROM users WHERE id = ?", (user_id,)
        ).fetchone()

        if user and user["role"] != "admin":
            db.execute(
                "DELETE FROM records WHERE username = ?", (user["username"],)
            )
            db.execute("DELETE FROM users WHERE id = ?", (user_id,))

    return redirect(url_for("records"))


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
