from flask import Blueprint
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import flash

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from database import get_db_connection

auth = Blueprint('auth', __name__)


# =========================
# REGISTER
# =========================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email=%s
                """,
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:
                flash('This email is already registered. Please sign in.', 'error')
                return redirect('/register')

            query = """
            INSERT INTO users
            (
                first_name,
                last_name,
                email,
                password_hash,
                phone,
                role_id
            )

            VALUES
            (%s,%s,%s,%s,%s,%s)
            """

            values = (
                first_name,
                last_name,
                email,
                hashed_password,
                phone,
                2
            )

            cursor.execute(query, values)

            conn.commit()

            flash('Account created successfully! Please sign in.', 'success')
            return redirect('/login')

        except Exception as e:
            flash(f'Registration error: {str(e)}', 'error')
            return redirect('/register')

        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")


# =========================
# LOGIN
# =========================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:

            if check_password_hash(
                user["password_hash"],
                password
            ):

                session["user_id"] = user["user_id"]
                session["user_name"] = user["first_name"]

                return redirect('/profile')

        flash('Invalid email or password. Please try again.', 'error')
        return redirect('/login')

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@auth.route("/logout")
def logout():

    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect('/login')