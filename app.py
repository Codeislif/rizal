
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-before-deployment"

DATABASE = Path(__file__).with_name("rizal_learning.db")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    db = get_db()

    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'
        );

        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            content TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    # Create demonstration accounts only if they do not exist.
    accounts = [
        ("Administrator", "admin", "admin123", "admin"),
        ("Demo Student", "student", "student123", "student")
    ]

    for name, username, password, role in accounts:
        exists = db.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()

        if not exists:
            db.execute(
                """INSERT INTO users (name, username, password, role)
                   VALUES (?, ?, ?, ?)""",
                (name, username, generate_password_hash(password), role)
            )

    # Starter educational modules.
    starter_modules = [
        (
            "Early Life and Childhood",
            "Discover Rizal's family and birthplace.",
            """José Protasio Rizal Mercado y Alonso Realonda was born
on June 19, 1861, in Calamba, Laguna.

He was the seventh of eleven children of Francisco Mercado and
Teodora Alonso Realonda. His family valued education, reading,
and discipline. From an early age, Rizal showed an interest in
literature, drawing, and learning."""
        ),
        (
            "Education and Achievements",
            "Learn about Rizal's studies and interests.",
            """Rizal studied in Biñan and later attended the Ateneo
Municipal de Manila and the University of Santo Tomas.

He pursued medical studies and specialized in ophthalmology.
He continued his education in Europe, including in Madrid,
and developed interests in languages, literature, science,
and the arts. He believed education could help improve society."""
        ),
        (
            "Noli Me Tangere",
            "Explore Rizal's influential first novel.",
            """Noli Me Tangere was published in Berlin, Germany, in
1887. The novel portrayed abuses and social problems during
Spanish colonial rule.

Its characters and events encouraged readers to reflect on
injustice and inequality. The book became an important work
in the development of Filipino national consciousness."""
        ),
        (
            "El Filibusterismo",
            "Discover the sequel to Noli Me Tangere.",
            """El Filibusterismo was published in Ghent, Belgium,
in 1891. It is the sequel to Noli Me Tangere.

The novel follows Simoun, the transformed identity of
Crisostomo Ibarra. It explores oppression, revenge, and
the consequences of injustice under colonial rule."""
        ),
        (
            "Exile in Dapitan",
            "Learn about Rizal's community service.",
            """In 1892, Rizal was exiled to Dapitan in Mindanao.
During his exile, he practiced medicine, taught students,
worked on community projects, and studied nature.

His activities showed his commitment to education,
health care, and improving community life."""
        ),
        (
            "Death and Legacy",
            "Understand Rizal's lasting influence.",
            """Rizal was executed on December 30, 1896, at Bagumbayan,
now part of Rizal Park in Manila.

His writings and advocacy for peaceful reform made him a
major figure in Philippine history. Today, he is widely
honored as the Philippine national hero. Rizal Day is
observed every December 30."""
        )
    ]

    count = db.execute("SELECT COUNT(*) AS total FROM modules").fetchone()["total"]

    if count == 0:
        db.executemany(
            """INSERT INTO modules (title, description, content)
               VALUES (?, ?, ?)""",
            starter_modules
        )

    db.commit()
    db.close()


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))

        if session.get("role") != "admin":
            flash("Administrator access is required.", "error")
            return redirect(url_for("index"))

        return function(*args, **kwargs)
    return wrapper


@app.route("/")
@login_required
def index():
    db = get_db()

    modules = db.execute(
        "SELECT * FROM modules ORDER BY id"
    ).fetchall()

    records = db.execute(
        """SELECT * FROM records
           WHERE user_id = ?
           ORDER BY id DESC""",
        (session["user_id"],)
    ).fetchall()

    best_score = max(
        (round(record["score"] / record["total"] * 100)
         for record in records if record["total"] > 0),
        default=0
    )

    db.close()

    return render_template(
        "index.html",
        modules=modules,
        records=records,
        best_score=best_score
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            return redirect(url_for("index"))

        flash("Incorrect username or password.", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not username or len(password) < 6:
            flash("Complete all fields. Password must be at least 6 characters.", "error")
            return render_template("register.html")

        if not all(c.isalnum() or c in "._-" for c in username):
            flash("Username may contain letters, numbers, dots, underscores, and hyphens only.", "error")
            return render_template("register.html")

        db = get_db()

        try:
            db.execute(
                """INSERT INTO users (name, username, password, role)
                   VALUES (?, ?, ?, 'student')""",
                (name, username, generate_password_hash(password))
            )
            db.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("That username is already registered.", "error")

        finally:
            db.close()

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/quiz", methods=["POST"])
@login_required
def save_quiz():
    # Do not trust the score sent by the browser.
    # Recalculate it on the server from the answer choices.
    questions = [
        {"answer": 0},
        {"answer": 1},
        {"answer": 2},
        {"answer": 0},
        {"answer": 3},
        {"answer": 1},
        {"answer": 0},
        {"answer": 2},
        {"answer": 3},
        {"answer": 0}
    ]

    submitted = request.form.getlist("answers")
    total = len(questions)
    score = sum(
        1 for index, question in enumerate(questions)
        if index < len(submitted)
        and submitted[index].isdigit()
        and int(submitted[index]) == question["answer"]
    )

    db = get_db()
    db.execute(
        """INSERT INTO records (user_id, activity, score, total)
           VALUES (?, 'Quiz', ?, ?)""",
        (session["user_id"], score, total)
    )
    db.commit()
    db.close()

    flash(f"Quiz completed! Your score is {score}/{total}.", "success")
    return redirect(url_for("index") + "#records")


@app.route("/admin/module/add", methods=["POST"])
@admin_required
def add_module():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    content = request.form.get("content", "").strip()

    if title and description and content:
        db = get_db()
        db.execute(
            """INSERT INTO modules (title, description, content)
               VALUES (?, ?, ?)""",
            (title, description, content)
        )
        db.commit()
        db.close()
        flash("Learning module added.", "success")
    else:
        flash("Please complete all module fields.", "error")

    return redirect(url_for("index") + "#admin")


@app.route("/admin/module/delete/<int:module_id>", methods=["POST"])
@admin_required
def delete_module(module_id):
    db = get_db()
    db.execute("DELETE FROM modules WHERE id = ?", (module_id,))
    db.commit()
    db.close()

    flash("Module deleted.", "success")
    return redirect(url_for("index") + "#admin")


@app.route("/admin/student/delete/<int:user_id>", methods=["POST"])
@admin_required
def delete_student(user_id):
    if user_id == session["user_id"]:
        flash("You cannot delete your own administrator account.", "error")
        return redirect(url_for("index") + "#admin")

    db = get_db()

    user = db.execute(
        "SELECT role FROM users WHERE id = ?", (user_id,)
    ).fetchone()

    if user and user["role"] == "student":
        db.execute("DELETE FROM records WHERE user_id = ?", (user_id,))
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        flash("Student account and records deleted.", "success")

    db.close()
    return redirect(url_for("index") + "#admin")


@app.route("/admin")
@admin_required
def admin_dashboard():
    return redirect(url_for("index") + "#admin")


@app.context_processor
def inject_admin_data():
    if session.get("role") != "admin":
        return {}

    db = get_db()
    students = db.execute(
        "SELECT id, name, username, role FROM users ORDER BY id"
    ).fetchall()

    all_records = db.execute(
        """SELECT records.*, users.name, users.username
           FROM records JOIN users ON records.user_id = users.id
           ORDER BY records.id DESC"""
    ).fetchall()

    student_count = db.execute(
        "SELECT COUNT(*) AS total FROM users WHERE role = 'student'"
    ).fetchone()["total"]

    module_count = db.execute(
        "SELECT COUNT(*) AS total FROM modules"
    ).fetchone()["total"]

    attempt_count = db.execute(
        "SELECT COUNT(*) AS total FROM records"
    ).fetchone()["total"]

    db.close()

    return {
        "admin_students": students,
        "all_records": all_records,
        "student_count": student_count,
        "module_count": module_count,
        "attempt_count": attempt_count
    }


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
