from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
import hashlib

app = Flask(__name__)
app.secret_key = "mysecretkey"


# ---------------- DATABASE SETUP ----------------
def create_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

create_database()


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 🔐 hash password before checking
        password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["username"] = username
            session["role"] = user[3]

            # Generate OTP
            otp = random.randint(1000, 9999)
            session["otp"] = otp

            print("Your OTP is:", otp)

            return redirect("/otp")
        else:
            return "Invalid username or password"

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 🔐 hash password before storing
        password = hashlib.sha256(password.encode()).hexdigest()

        role = request.form["role"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


# ---------------- OTP VERIFY ----------------
@app.route("/otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered_otp = request.form["otp"]

        if int(entered_otp) == session.get("otp"):
            return redirect("/dashboard")
        else:
            return "Incorrect OTP"

    return render_template("otp.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", role=session["role"])
    return redirect("/")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)