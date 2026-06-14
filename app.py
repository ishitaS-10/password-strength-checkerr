from flask import Flask, render_template, request  # type: ignore[import]
import sqlite3
import hashlib
import re
import random
import string

app = Flask(__name__)

# -------- PASSWORD CHECK --------
def check_password_strength(password):
    score = 0
    feedback = []

    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        feedback.append("Use at least 8 characters")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Add uppercase letter")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Add lowercase letter")

    if re.search(r"[0-9]", password):
        score += 1
    else:
        feedback.append("Add numbers")

    if re.search(r"[!@#$%^&*]", password):
        score += 2
    else:
        feedback.append("Add special character")

    return score, feedback

# -------- PASSWORD GENERATOR --------
def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(12))

# -------- HASH --------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -------- DATABASE --------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

# -------- ROUTES --------
@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    feedback = []
    suggestion = None

    if request.method == 'POST':
        password = request.form['password']
        score, feedback = check_password_strength(password)

        if score >= 6:
            result = "Strong ✅"
        elif score >= 4:
            result = "Moderate ⚠️"
        else:
            result = "Weak ❌"
            suggestion = generate_password()

    return render_template("index.html", result=result, feedback=feedback, suggestion=suggestion)

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = hash_password(request.form['password'])

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

    return "User Registered Successfully!"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)