import os

from cryptography.fernet import Fernet
from cs50 import SQL
import datetime
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import api_key_validation, apology, encrypt_key, get_fernet_instance, login_required, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///resi.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show the previously submitted resumes"""
    return apology("TODO", 400)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/api_key", methods=["GET", "POST"])
@login_required
def api_key():
    """Allow users to set up their API Key"""
    if request.method == "POST":
        # Ensure API Key was submitted
        if not request.form.get("user_api_key"):
            return apology("must provide API Key", 400)
        
        # Validate user's API Key        
        if not api_key_validation(request.form.get("user_api_key")):
            return apology("must provide a valid API Key", 400)
        
        # Get the ferenet instance to encrypt the API key
        # fernet_instance = get_fernet_instance()
        
        ###TEST###
        with open('/Users/jadonvanyo/Desktop/cs50/final_project/secret_keys/secret_key.txt', 'r', encoding='utf-8') as file:
            # Generate fernet instance to encrypt the user's secret key from secret key in file
            fernet_instance = Fernet(file.read().strip())
        
        # Update the users encrypted API key in the users database
        db.execute(
            "UPDATE users SET api_key = ? WHERE id = ?;",
            encrypt_key(request.form.get("user_api_key"), fernet_instance), session["user_id"]
        )
        
        # Redirect to the main page
        return redirect("/")
    
    else:
        return render_template("api_key.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for email
        rows = db.execute(
            "SELECT * FROM users WHERE email = ?", request.form.get("email")
        )

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid email and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # TODO: Set OpenAi API to NULL
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        # Ensure password and confirmation of password match
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords must match", 400)

        # Query database to see if the email already exists
        elif db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email")):
            return apology("email already taken", 400)

        # Insert new user into the database and remember which user has logged in
        session["user_id"] = db.execute("INSERT INTO users (email, hash) VALUES(?, ?);", 
            request.form.get("email"), generate_password_hash(request.form.get("password")))

        # TODO: Delete this
        # Remember which user has logged in
        # session["user_id"] = id

        # Redirect to the API key page
        return redirect("/api_key")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    