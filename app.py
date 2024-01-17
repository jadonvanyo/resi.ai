import os

import openai
from cs50 import SQL
import datetime
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import api_key_validation, apology, decrypt_key, encrypt_key, get_fernet_instance, get_response, login_required, usd

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


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Main feature to tailor the user's resume"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure the user entered a job title
        if not request.form.get("jobtitle"):
            return apology("missing target job title", 400)

        # Ensure that the user entered an industry
        elif not request.form.get("industry"):
            return apology("missing target industry", 400)
        
        # Ensure that the user entered a company
        elif not request.form.get("company"):
            return apology("missing target company", 400)
        
        # Ensure that the user entered their current/previous job
        elif not request.form.get("prevjob"):
            return apology("missing current/previous job", 400)
        
        # Ensure that the user entered a job description
        elif not request.form.get("jobdescription"):
            return apology("missing job description", 400)
        
        # Ensure that the user entered a resume or selected to use their saved resume
        elif not request.form.get("resume") and not request.form.get("savedresume"):
            return apology("missing resume", 400)
        
        # Ensure the user has not entered a resume and selected to use a saved resume
        elif request.form.get("resume") and request.form.get("savedresume"):
            return apology("cannot use 2 resumes at once", 400)
        
        # Ensure the user has a resume saved if they selected to use a saved resume and did not enter a resume
        elif not request.form.get("resume") and request.form.get("savedresume"):
            # SELECT the user's resume from users
            resume = db.execute(
                "SELECT resume FROM users WHERE id = ?;", session["user_id"]
            )
            # Ensure the user has a resume saved in users
            if not resume:
                return apology("no saved resume", 400)
        
        # Store resume if the user entered a resume
        elif request.form.get("resume") and not request.form.get("savedresume"):
            resume = request.form.get("resume")
        
        # SELECT the user's encrypted API key from users
        encrypted_api_key = (db.execute(
            "SELECT api_key FROM users WHERE id = ?;", session["user_id"]
        ))[0]["api_key"]
        
        # Ensure the user has entered an API key
        if not encrypted_api_key:
            return apology("no saved api key", 400)
        
        # TODO: Check that the user entered a sufficiently long resume

        # TODO: Redirect the user to a loading screen while the functions work (use AJAX)
        
        # TODO: Move all of this to helpers.py
        
        # Create the first prompt for API call to get most important 
        prompt = f"""
            You are an expert resume writer with over 20 years of experience working with
            job seekers trying to land a role in {request.form.get("industry")}.
            Highlight the 3 most important responsibilities in this job description:
            Job Description:
            '''
            {request.form.get("jobdescription")}
            '''
            """
        
        # 
        imp_resp = get_response(decrypt_key(encrypted_api_key, get_fernet_instance()), prompt, 0.1)
        
        prompt = f"""
            You are an expert resume writer with over 20 years of experience working with
            job seekers trying to land a role in {request.form.get("industry")}. You specialize in helping
            write resumes for a {request.form.get("prevjob")} looking to transition to a new career path 
            in {request.form.get("industry")}.

            Based on these 3 most important responsibilities from the job description,
            please tailor my resume for this {request.form.get("jobtitle")} position at
            {request.form.get("company")}. Do not make information up.

            3 Most important responsibilities: 
            '''
            {imp_resp}
            '''

            Resume:
            '''
            {resume}
            '''
            """
        
        tailored_resume = get_response(decrypt_key(encrypted_api_key, get_fernet_instance()), prompt, 0.5)
        
        prompt = f"""
            List out the differences between my original resume and the suggested draft \
            in table format with 2 columns: Original and Updated. Be specific and list out \
            exactly what was changed, down to the exact wording.

            My Original:
            '''
            {resume}
            '''

            Suggested Draft:
            '''
            {tailored_resume}
            '''
            """
        
        differences = get_response(decrypt_key(encrypted_api_key, get_fernet_instance()), prompt, 0.3)
        
        # TODO: Create new resume database
        
        # TODO: Save the new resume in a new resume database
        
        # Render a new page with the 3 key responsibilities, differences, and tailored resume
        return render_template("tailored_resume.html", imp_resp=imp_resp, differences=differences, tailored_resume=tailored_resume)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")
    

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/account")
@login_required
def account():
    # SELECT the user's email from users
    email = (db.execute("SELECT email FROM users WHERE id = ?", session["user_id"]))[0]["email"]
    
    # SELECT the user's encrypted API key from users
    encrypted_api_key = (db.execute(
            "SELECT api_key FROM users WHERE id = ?;", session["user_id"]
        ))[0]["api_key"]
    
    # Return the account page with all the required information added
    return render_template("account.html", email=email, api_key=decrypt_key(encrypted_api_key, get_fernet_instance()))


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
        
        # Get the fernet instance to encrypt the API key
        fernet_instance = get_fernet_instance()
        
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


@app.route("/price_estimator")
@login_required
def price_estimator():
    return render_template("price_estimator.html")


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
    