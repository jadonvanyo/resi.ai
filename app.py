import os

from cs50 import SQL
import datetime
from flask import Flask, jsonify, redirect, render_template, render_template_string, request, session
from flask_session import Session
import markdown
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import api_key_validation, apology, convert_imp_resp_to_html, decrypt_key, encrypt_key, get_differences, get_fernet_instance, get_imp_resp, get_tailored_resume, login_required, price_estimation, price_estimator_prompts, usd

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
            return jsonify({
                'status': 'error',
                'message': 'Missing target job title'
            })

        # Ensure that the user entered an industry
        elif not request.form.get("industry"):
            return jsonify({
                'status': 'error',
                'message': 'Missing target industry'
            })
        
        # Ensure that the user entered a company
        elif not request.form.get("company"):
            return jsonify({
                'status': 'error',
                'message': 'Missing target company'
                })
        
        # Ensure that the user entered their current/previous job
        elif not request.form.get("prevjob"):
            return jsonify({
                'status': 'error',
                'message': 'Missing current/previous job'
            })
        
        # Ensure that the user entered a job description
        elif not request.form.get("jobdescription"):
            return jsonify({
                'status': 'error',
                'message': 'Missing job description'
            })
            
        # Check that the user entered a sufficiently long job description
        elif len(request.form.get("jobdescription")) < 250:        
            return jsonify({
                'status': 'error',
                'message': 'Job Description too short'
            })
        
        # Ensure that the user entered a resume
        elif not request.form.get("resume"):
            return jsonify({
                'status': 'error',
                'message': 'Missing resume'
            })
        
        # Check that the user entered a sufficiently long resume
        elif len(request.form.get("resume")) < 1500:        
            return jsonify({
                'status': 'error',
                'message': 'Resume too short'
            })
        
        # Store resume if the user entered a resume
        resume = request.form.get("resume")
        
        # SELECT the user's encrypted API key from users
        encrypted_api_key = (db.execute(
            "SELECT api_key FROM users WHERE id = ?;", session["user_id"]
        ))[0]["api_key"]
        
        # Ensure the user has an API key
        if not encrypted_api_key:
            return jsonify({
                'status': 'error',
                'message': 'No API key saved'
            })
            
        # TODO: Token count checks to ensure none of the token counts exceed the limit
        
        # API call to get the 3 most important responsibilities from the description
        imp_resp = get_imp_resp(decrypt_key(encrypted_api_key, get_fernet_instance()), request.form.get("industry"), request.form.get("jobdescription"))
        
        # Convert the important responsibilities to html format
        imp_resp_html = convert_imp_resp_to_html(decrypt_key(encrypted_api_key, get_fernet_instance()), imp_resp)
        
        # API call to get tailored resume from user information
        tailored_resume = get_tailored_resume(
            decrypt_key(encrypted_api_key, get_fernet_instance()), 
            request.form.get("company"),
            imp_resp, 
            request.form.get("industry"),
            request.form.get("jobdescription"),
            request.form.get("jobtitle"),
            request.form.get("prevjob"), 
            resume
        )
        
        # TODO: Improve the differences comparison (Potentially eliminate this feature)
        differences = get_differences(decrypt_key(encrypted_api_key, get_fernet_instance()), resume, tailored_resume)
        
        # Change the markdown received from OpenAI to HTML
        differences_html = markdown.markdown(differences, extensions=['markdown.extensions.tables'])
        
        # TODO: Create new resume database 
        
        # TODO: Save the new resume in a new resume database (store the html versions)
        
        # Return the 3 key responsibilities, differences, and tailored resume to update the page
        return jsonify({
            'status': 'success',
            'message': 'Resume processed successfully',
            'imp_resp': render_template_string(imp_resp_html),
            'tailored_resume': render_template_string(tailored_resume),
            'differences': render_template_string(differences_html)
        })
        
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # SELECT the user's resume from users
        resume = (db.execute(
            "SELECT resume FROM users WHERE id = ?;", session["user_id"]
        ))[0]["resume"]
        
        return render_template("index.html", resume=resume)
    

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 400)
        
        # Ensure an API key was submitted
        elif not request.form.get("user_api_key"):
            return apology("must provide API Key", 400)
        
        # Check if the user entered a new password
        elif request.form.get("password") or request.form.get("confirmation"):
            # Determine if the password and confirmation do not match
            if request.form.get("password") != request.form.get("confirmation"):
                return apology("new password and confirmation must match", 403)
            
            # SELECT the users hash from users
            old_hash = (db.execute(
                "SELECT hash FROM users WHERE id = ?", session["user_id"]
            ))[0]["hash"]
            
            # Check if the password matches the password the user already has
            if check_password_hash(old_hash, request.form.get("password")):
                return apology("password already in use", 403)
            
            # UPDATE the user's password in users if all checks pass
            db.execute(
                "UPDATE users SET hash = ? WHERE id = ?;",
                generate_password_hash(request.form.get("password")), session["user_id"]
            )
        
        # Check if the user has entered an email that is different than their previous email
        elif request.form.get("email") != (db.execute("SELECT email FROM users WHERE id = ?", session["user_id"]))[0]["email"]:
            # UPDATE the user's email in users
            db.execute(
                "UPDATE users SET email = ? WHERE id = ?;",
                request.form.get("email"), session["user_id"]
            )
        
        # SELECT the user's encrypted API key from users
        encrypted_api_key = (db.execute(
                "SELECT api_key FROM users WHERE id = ?;", session["user_id"]
        ))[0]["api_key"]
            
        # Check if the user already has an API key saved
        if not encrypted_api_key:
             # Validate user's API Key
            if not api_key_validation(request.form.get("user_api_key")):
                return apology("must provide a valid API Key", 400)
            
            # Update the users encrypted API key in the users database
            db.execute(
                "UPDATE users SET api_key = ? WHERE id = ?;",
                encrypt_key(request.form.get("user_api_key"), get_fernet_instance()), session["user_id"]
            )
        
        # Check if the user has entered an API key different than the one previously in the database
        elif request.form.get("user_api_key") != decrypt_key(
            encrypted_api_key, get_fernet_instance()
        ):
             # Validate user's API Key
            if not api_key_validation(request.form.get("user_api_key")):
                return apology("must provide a valid API Key", 400)
            
            # Update the users encrypted API key in the users database
            db.execute(
                "UPDATE users SET api_key = ? WHERE id = ?;",
                encrypt_key(request.form.get("user_api_key"), get_fernet_instance()), session["user_id"]
            )
            
        # Check if the user entered a resume
        if request.form.get("resume") != (db.execute("SELECT resume FROM users WHERE id = ?", 
                session["user_id"]))[0]["resume"]:
            # Check that the user entered a sufficiently long resume
            if len(request.form.get("resume")) < 1500:
                return apology("resume too short", 400)
            # UPDATE the users resume in users
            else:
                db.execute(
                    "UPDATE users SET resume = ? WHERE id = ?;",
                    request.form.get("resume"), session["user_id"]
                )
        
        # After all updates are made, redirect the user to the updated account page
        return redirect("/account")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # SELECT the user's email from users
        email = (db.execute("SELECT email FROM users WHERE id = ?", session["user_id"]))[0]["email"]
        
        # SELECT the user's encrypted API key from users
        encrypted_api_key = (db.execute(
                "SELECT api_key FROM users WHERE id = ?;", session["user_id"]
        ))[0]["api_key"]
        
        # SELECT the user's resume from users
        resume = (db.execute(
            "SELECT resume FROM users WHERE id = ?;", session["user_id"]
        ))[0]["resume"]
        
        # Return an Account page without the API key
        if not encrypted_api_key:
            return render_template("account.html", email=email, user_api_key="", resume=resume)
            
        else:
            # Return the account page with all the required information added
            return render_template("account.html", email=email, user_api_key=decrypt_key(encrypted_api_key, get_fernet_instance()), resume=resume)


@app.route("/api_key", methods=["GET", "POST"])
@login_required
def api_key():
    """Allow users to set up and update their API Key"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure API Key was submitted
        if not request.form.get("user_api_key"):
            return apology("must provide API Key", 400)
        
        # SELECT the user's encrypted API key from users
        encrypted_api_key = (db.execute(
                "SELECT api_key FROM users WHERE id = ?;", session["user_id"]
        ))[0]["api_key"]
        
        # Check if the user does not have an API key
        if not encrypted_api_key:
            # Validate user's API Key        
            if not api_key_validation(request.form.get("user_api_key")):
                return apology("must provide a valid API Key", 400)
            
            # Update the users encrypted API key in the users database
            db.execute(
                "UPDATE users SET api_key = ? WHERE id = ?;",
                encrypt_key(request.form.get("user_api_key"), get_fernet_instance()), session["user_id"]
            )

        # Check if the user has entered an API key different than the one previously in the database
        elif request.form.get("user_api_key") != decrypt_key(
            encrypted_api_key, get_fernet_instance()
        ):
             # Validate user's API Key
            if not api_key_validation(request.form.get("user_api_key")):
                return apology("must provide a valid API Key", 400)
            
            # Update the users encrypted API key in the users database
            db.execute(
                "UPDATE users SET api_key = ? WHERE id = ?;",
                encrypt_key(request.form.get("user_api_key"), get_fernet_instance()), session["user_id"]
            )
            
        # Redirect to the main page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # SELECT the user's encrypted API key from users
        encrypted_api_key = (db.execute(
                "SELECT api_key FROM users WHERE id = ?;", session["user_id"]
        ))[0]["api_key"]

        # Return an Account page without the API key
        if not encrypted_api_key:
            return render_template("api_key.html")
            
        else:
            # Return the account page with the API key
            return render_template("api_key.html", user_api_key=decrypt_key(encrypted_api_key, get_fernet_instance()))
        

@app.route("/history")
@login_required
def history():
    """Present the last 5 resumes the user has generated"""
    # TODO: Display the last 5 resumes that the user has generated
    # TODO: Display the date, name of the company, and maybe differences      
    return apology("TODO", 403)

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
    
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/price_estimator", methods=["GET", "POST"])
@login_required
def price_estimator():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure a job description was entered
        if not request.form.get("jobdescription"):
            return apology("must provide job description", 400)
        
        # Ensure a resume was submitted
        elif not request.form.get("resume"):
            return apology("must provide a resume", 400)
        
        # Check that the user entered a sufficiently long resume
        elif len(request.form.get("resume")) < 1500:
                return apology("resume too short", 400)
            
        # SELECT the user's encrypted API key from users
        encrypted_api_key = (db.execute(
            "SELECT api_key FROM users WHERE id = ?;", session["user_id"]
        ))[0]["api_key"]
        
        # Ensure the user has entered an API key
        if not encrypted_api_key:
            return apology("no saved api key", 400)
        
        # Call function to create the example prompts required a tailor the resume
        price_estimate_inputs, price_estimate_outputs = price_estimator_prompts(request.form.get("jobdescription"), request.form.get("resume"))
        
        # Calculate the number of price needed for the total prompt
        total_cost = price_estimation(decrypt_key(encrypted_api_key, get_fernet_instance()), price_estimate_inputs, price_estimate_outputs)
        
        # Return template with the price estimate
        return render_template("price_estimate.html", total_cost=total_cost)
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # SELECT the user's resume from users
        resume = (db.execute(
            "SELECT resume FROM users WHERE id = ?;", session["user_id"]
        ))[0]["resume"]
        return render_template("price_estimator.html", resume=resume)


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

        # Redirect to the API key page
        return redirect("/api_key")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    