# import os

from cs50 import SQL
import datetime
from flask import Flask, jsonify, redirect, render_template, render_template_string, request, session
from flask_session import Session
import markdown
import re
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import api_key_validation, apology, decrypt_key, encrypt_key, get_differences, get_fernet_instance, get_imp_resp, get_tailored_cover_letter_full, get_tailored_cover_letter_partial, get_tailored_resume, login_required, price_estimation, price_estimator_prompts, usd

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
        
        # Ensure the job title is not too long
        elif len(request.form.get("jobtitle")) > 50:
            return jsonify({
                'status': 'error',
                'message': 'Target Job Title too long'
            })

        # Ensure that the user entered an industry
        elif not request.form.get("industry"):
            return jsonify({
                'status': 'error',
                'message': 'Missing target industry'
            })
            
        # Ensure the industry is not too long
        elif len(request.form.get("industry")) > 50:
            return jsonify({
                'status': 'error',
                'message': 'Target Industry too long'
            })
        
        # Ensure that the user entered a company
        elif not request.form.get("company"):
            return jsonify({
                'status': 'error',
                'message': 'Missing target company'
            })
            
        # Ensure the company name is not too long
        elif len(request.form.get("company")) > 50:
            return jsonify({
                'status': 'error',
                'message': 'Target Company too long'
            })
        
        # Ensure that the user entered a job description
        elif not request.form.get("jobdescription"):
            return jsonify({
                'status': 'error',
                'message': 'Missing job description'
            })
            
        # Check if the job description is too short
        elif len(request.form.get("jobdescription")) < 500:        
            return jsonify({
                'status': 'error',
                'message': f'Job Description too short. Characters: {len(request.form.get("jobdescription"))} Minimum: 500'
            })
            
        # Check that the job description is too long
        elif len(request.form.get("jobdescription")) > 4000:        
            return jsonify({
                'status': 'error',
                'message': f'Job Description too long. Characters: {len(request.form.get("jobdescription"))} Limit: 4000'
            })
        
        # Ensure that the user entered a resume
        elif not request.form.get("resume"):
            return jsonify({
                'status': 'error',
                'message': 'Missing resume'
            })
        
        # Check that the resume is long enough
        elif len(request.form.get("resume")) < 1500:        
            return jsonify({
                'status': 'error',
                'message': f'Resume too short. Characters: {len(request.form.get("resume"))} Minimum: 1500'
            })
            
        # Check that the resume is short enough
        elif len(request.form.get("resume")) > 4500:        
            return jsonify({
                'status': 'error',
                'message': f'Resume too long. Characters: {len(request.form.get("resume"))} Limit: 4500'
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
        
        # API call to get the 3 most important responsibilities from the description
        imp_resp = get_imp_resp(decrypt_key(encrypted_api_key, get_fernet_instance()),
                                request.form.get("industry"), request.form.get("jobdescription"))
        
        # Add title to the section and convert important responsibilities to HTML using markdown
        imp_resp_html = "<h2>Important Responsibilities</h2>" + markdown.markdown(imp_resp)
        
        # API call to get tailored resume from user information
        tailored_resume = get_tailored_resume(
            decrypt_key(encrypted_api_key, get_fernet_instance()), 
            request.form.get("company"),
            imp_resp, 
            request.form.get("industry"),
            request.form.get("jobdescription"),
            request.form.get("jobtitle"),
            resume
        )
        
        # Format the tailored resume for HTML
        tailored_resume_html = "<h2>Tailored Resume</h2>" + tailored_resume
        
        # API call to get the differences comparison between old and new resumes
        differences = get_differences(decrypt_key(encrypted_api_key, get_fernet_instance()), resume, tailored_resume)
        
        # Change the markdown received from OpenAI to HTML
        differences_html = markdown.markdown(differences, extensions=['markdown.extensions.tables'])
        
        # Add stripped table formatting to the table
        differences_html = re.sub(r'<table>', '<table class="table table-striped">', differences_html)
        
        # Add bold column headers to the table and a title for the section
        differences_html = "<h2>Differences</h2>" + re.sub(r'<th>', '<th scope="col">', differences_html)
        
        # Create name for the resume to be saved in the database
        resume_name = request.form.get("company") + " " + request.form.get("jobtitle") + " Resume"
        
        # SELECT all saved resumes/cover letters to see if there is more than 4
        if db.execute(
            'SELECT COUNT(*) FROM history WHERE user_id = ?;',
            session["user_id"]
        )[0]['COUNT(*)'] > 4:
            # If more than 4, UPDATE the oldest entry in history database with the newest entry
            db.execute(
                '''UPDATE history 
                SET document_name = ?, company = ?, job_title = ?, document = ?, datetime = ?
                WHERE user_id = ? AND datetime = (SELECT MIN(datetime) FROM history WHERE user_id = ?)
                ''',
                resume_name, 
                request.form.get("company"), 
                request.form.get("jobtitle"), 
                tailored_resume, 
                datetime.datetime.now(), 
                session["user_id"],
                session["user_id"]
            )
            
        # If not past the 5 document limit, INSERT the data into history
        else:
            db.execute(
                'INSERT INTO history (user_id, document_name, company, job_title, document, datetime) VALUES(?, ?, ?, ?, ?, ?);',
                session["user_id"], resume_name, request.form.get("company"), 
                request.form.get("jobtitle"), tailored_resume, datetime.datetime.now()
            )
        
        # Return the 3 key responsibilities, differences, and tailored resume to update the page
        return jsonify({
            'status': 'success',
            'message': 'Resume processed successfully',
            'imp_resp': render_template_string(imp_resp_html),
            'tailored_resume': render_template_string(tailored_resume_html),
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
    """Account page for the users to view and update their profile information"""

    # Empty successful update variable to record what the user has updated
    success_response = ""
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure email was submitted
        if not request.form.get("email"):
            return jsonify({
                'status': 'error',
                'message': 'Must provide an Email.'
            })
            # return apology("must provide email", 400)
        
        # Ensure an API key was submitted
        elif not request.form.get("user_api_key"):
            return jsonify({
                'status': 'error',
                'message': 'Must provide API Key.'
            })
            # return apology("must provide API Key", 400)
        
        # Check if the user entered a new password
        elif request.form.get("password") or request.form.get("confirmation"):
            # Determine if the password and confirmation do not match
            if request.form.get("password") != request.form.get("confirmation"):
                return jsonify({
                    'status': 'error',
                    'message': 'New password and confirmation must match.'
                })
                # return apology("new password and confirmation must match", 403)
            
            # SELECT the users hash from users
            old_hash = (db.execute(
                "SELECT hash FROM users WHERE id = ?", session["user_id"]
            ))[0]["hash"]
            
            # Check if the password matches the password the user already has
            if check_password_hash(old_hash, request.form.get("password")):
                return jsonify({
                    'status': 'error',
                    'message': 'Password already in use.'
                })
                # return apology("password already in use", 403)
            
            # UPDATE the user's password in users if all checks pass
            db.execute(
                "UPDATE users SET hash = ? WHERE id = ?;",
                generate_password_hash(request.form.get("password")), session["user_id"]
            )
            
            # Add the password to the successful update variable
            success_response += "Password"
        
        # Check if the user has entered an email that is different than their previous email
        if request.form.get("email") != (db.execute("SELECT email FROM users WHERE id = ?", session["user_id"]))[0]["email"]:
            # UPDATE the user's email in users
            db.execute(
                "UPDATE users SET email = ? WHERE id = ?;",
                request.form.get("email"), session["user_id"]
            )
            
            # Add the email to the successful response if updated
            if not success_response:
                success_response += "Email"
            
            else:
                success_response += ", Email"
        
        # SELECT the user's encrypted API key from users
        encrypted_api_key = (db.execute(
            "SELECT api_key FROM users WHERE id = ?;", session["user_id"]
        ))[0]["api_key"]
            
        # Check if the user already has an API key saved
        if not encrypted_api_key:
            # Validate user's API Key
            if not api_key_validation(request.form.get("user_api_key")):
                return jsonify({
                    'status': 'error',
                    'message': 'Must provide a valid API Key.'
                })
                # return apology("must provide a valid API Key", 400)
            
            # Update the users encrypted API key in the users database
            db.execute(
                "UPDATE users SET api_key = ? WHERE id = ?;",
                encrypt_key(request.form.get("user_api_key"), get_fernet_instance()), session["user_id"]
            )
            
            # Add the API Key to the successful response if updated
            if not success_response:
                success_response += "API Key"
            
            else:
                success_response += ", API Key"
        
        # Check if the user has entered an API key different than the one previously in the database
        elif request.form.get("user_api_key") != decrypt_key(
            encrypted_api_key, get_fernet_instance()
        ):
            # Validate user's API Key
            if not api_key_validation(request.form.get("user_api_key")):
                return jsonify({
                    'status': 'error',
                    'message': 'Must provide a valid API Key.'
                })
                # return apology("must provide a valid API Key", 400)
            
            # Update the users encrypted API key in the users database
            db.execute(
                "UPDATE users SET api_key = ? WHERE id = ?;",
                encrypt_key(request.form.get("user_api_key"), get_fernet_instance()), session["user_id"]
            )
            
            # Add the API Key to the successful response if updated
            if not success_response:
                success_response += "API Key"
            
            else:
                success_response += ", API Key"
            
        # Check if the user entered a resume
        if request.form.get("resume") != (db.execute("SELECT resume FROM users WHERE id = ?", 
                                          session["user_id"]))[0]["resume"]:
            # Check that the user entered a sufficiently long resume
            if len(request.form.get("resume")) < 1500:
                return jsonify({
                    'status': 'error',
                    'message': 'Resume too short.'
                })
                # return apology("resume too short", 400)
            # UPDATE the users resume in users
            else:
                db.execute(
                    "UPDATE users SET resume = ? WHERE id = ?;",
                    request.form.get("resume"), session["user_id"]
                )
                
            # Add resume to the successful response if updated
            if not success_response:
                success_response += "Resume"
            
            else:
                success_response += ", Resume"
        
        # Redirect the user to the same page if no updates were made
        if not success_response:
            return redirect("/account")
        # Send alert message to the user with all the updates made
        else:
            success_response += " successfully updated!"
            return jsonify({
                'status': 'success',
                'message': success_response
            })
        # return redirect("/account")
    
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
            return jsonify({
                'status': 'error',
                'message': 'Must provide API Key.'
            })
        
        # SELECT the user's encrypted API key from users
        encrypted_api_key = (db.execute(
            "SELECT api_key FROM users WHERE id = ?;", session["user_id"]
        ))[0]["api_key"]
        
        # Check if the user does not have an API key
        if not encrypted_api_key:
            # Validate user's API Key        
            if not api_key_validation(request.form.get("user_api_key")):
                return jsonify({
                    'status': 'error',
                    'message': 'Must provide a valid API key.'
                })
            
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
                return jsonify({
                    'status': 'error',
                    'message': 'Must provide a Valid API Key.'
                })
            
            # Update the users encrypted API key in the users database
            db.execute(
                "UPDATE users SET api_key = ? WHERE id = ?;",
                encrypt_key(request.form.get("user_api_key"), get_fernet_instance()), session["user_id"]
            )
        
        # Send alert to the user that their API key was successfully updated
        return jsonify({
            'status': 'success',
        })

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
    # SELECT the document history for a user
    history = db.execute(
        "SELECT * FROM history WHERE user_id= ? ORDER BY datetime DESC;",
        session["user_id"]
    )
    # Display the last 5 documents that the user has generated 
    return render_template("history.html", history=history)


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
    """Allow the user to estimate how much it will cost to generate a resume"""
    # TODO: Try to figure out why this is so off
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure a job description was entered
        if not request.form.get("jobdescription"):
            return apology("must provide job description", 400)
        
        # Check that the job description is long enough
        elif len(request.form.get("jobdescription")) < 500:
            return apology("job description too short", 400)
        
        # Check that the job description is not too long
        elif len(request.form.get("jobdescription")) > 4000:
            return apology("job description too long", 400)
        
        # Ensure a resume was submitted
        elif not request.form.get("resume"):
            return apology("must provide a resume", 400)
        
        # Check that the resume is long enough
        elif len(request.form.get("resume")) < 1500:
            return apology("resume too short", 400)
            
        # Check that the resume is not too long
        elif len(request.form.get("resume")) > 4500:
            return apology("resume too long", 400)
            
        # SELECT the user's encrypted API key from users
        encrypted_api_key = (db.execute(
            "SELECT api_key FROM users WHERE id = ?;", session["user_id"]
        ))[0]["api_key"]
        
        # Ensure the user has entered an API key
        if not encrypted_api_key:
            return apology("no saved api key", 400)
        
        # Call function to create the example prompts required a tailor the resume
        price_estimate_inputs, price_estimate_outputs = price_estimator_prompts(
            request.form.get("jobdescription"), request.form.get("resume"))
        
        # Calculate the price needed for the total prompt
        total_cost = price_estimation(decrypt_key(encrypted_api_key, get_fernet_instance()),
                                      price_estimate_inputs, price_estimate_outputs)
        
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
    """Register a new user"""
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


@app.route("/tailored_cover_letter", methods=["GET", "POST"])
@login_required
def tailored_cover_letter():
    """Create a tailored cover letter based on the user's inputs"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure the user entered their previous job title
        if not request.form.get("prevjob"):
            return jsonify({
                'status': 'error',
                'message': 'Missing previous/current job title'
            })
            
        # Ensure the previous/current job title is not too long
        elif len(request.form.get("prevjob")) > 50:
            return jsonify({
                'status': 'error',
                'message': 'Target Job Title too long'
            })
            
        # Ensure the user entered a job title
        elif not request.form.get("jobtitle"):
            return jsonify({
                'status': 'error',
                'message': 'Missing target job title'
            })
        
        # Ensure the job title is not too long
        elif len(request.form.get("jobtitle")) > 50:
            return jsonify({
                'status': 'error',
                'message': 'Target Job Title too long'
            })
        
        # Ensure that the user entered a company
        elif not request.form.get("company"):
            return jsonify({
                'status': 'error',
                'message': 'Missing target company'
            })
            
        # Ensure the company name is not too long
        elif len(request.form.get("company")) > 50:
            return jsonify({
                'status': 'error',
                'message': 'Target Company too long'
            })
        
        # Ensure that the user entered a job description
        elif not request.form.get("jobdescription"):
            return jsonify({
                'status': 'error',
                'message': 'Missing job description'
            })
            
        # Check if the job description is too short
        elif len(request.form.get("jobdescription")) < 500:        
            return jsonify({
                'status': 'error',
                'message': f'Job Description too short. Characters: {len(request.form.get("jobdescription"))} Minimum: 500'
            })
            
        # Check that the job description is too long
        elif len(request.form.get("jobdescription")) > 4000:        
            return jsonify({
                'status': 'error',
                'message': f'Job Description too long. Characters: {len(request.form.get("jobdescription"))} Limit: 4000'
            })
        
        # Ensure that the user entered a resume
        elif not request.form.get("resume"):
            return jsonify({
                'status': 'error',
                'message': 'Missing resume'
            })
        
        # Check that the resume is long enough
        elif len(request.form.get("resume")) < 1500:        
            return jsonify({
                'status': 'error',
                'message': f'Resume too short. Characters: {len(request.form.get("resume"))} Minimum: 1500'
            })
            
        # Check that the resume is short enough
        elif len(request.form.get("resume")) > 4500:        
            return jsonify({
                'status': 'error',
                'message': f'Resume too long. Characters: {len(request.form.get("resume"))} Limit: 4500'
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
        
        # Check if the user wanted a full resume
        if request.form.get("coverletter") == "full":
            # API call to create a full cover letter based on the user's inputs
            tailored_cover_letter = get_tailored_cover_letter_full(
                decrypt_key(encrypted_api_key, get_fernet_instance()), 
                request.form.get("company"), 
                request.form.get("jobdescription"), 
                request.form.get("jobtitle"), 
                request.form.get("prevjob"), 
                resume,
            )
            format = ' Full '
        
        # Else, assume the user wants a partial cover letter
        else:
            # API call to create a partial cover letter based on the user's inputs
            tailored_cover_letter = get_tailored_cover_letter_partial(
                decrypt_key(encrypted_api_key, get_fernet_instance()), 
                request.form.get("company"), 
                request.form.get("jobdescription"), 
                request.form.get("jobtitle"), 
                request.form.get("prevjob"), 
                resume,
            )
            format = ' Partial '
            
        # Create name for the cover letter to be saved in the database
        cover_letter_name = request.form.get("company") + " " + request.form.get("jobtitle") + format + "Cover Letter"
        
        # SELECT all saved resumes/cover letters to see if there is more than 4
        if db.execute(
            'SELECT COUNT(*) FROM history WHERE user_id = ?;',
            session["user_id"]
        )[0]['COUNT(*)'] > 4:
            # If more than 4, UPDATE the oldest entry in history database with the newest entry
            db.execute(
                '''UPDATE history 
                SET document_name = ?, company = ?, job_title = ?, document = ?, datetime = ?
                WHERE user_id = ? AND datetime = (SELECT MIN(datetime) FROM history WHERE user_id = ?)
                ''',
                cover_letter_name, 
                request.form.get("company"), 
                request.form.get("jobtitle"), 
                tailored_cover_letter, 
                datetime.datetime.now(), 
                session["user_id"],
                session["user_id"]
            )
            
        # If not past the 5 document limit, INSERT the data into history
        else:
            db.execute(
                'INSERT INTO history (user_id, document_name, company, job_title, document, datetime) VALUES(?, ?, ?, ?, ?, ?);',
                session["user_id"], cover_letter_name, request.form.get("company"), 
                request.form.get("jobtitle"), tailored_cover_letter, datetime.datetime.now()
            )
        
        # Return the tailored resume to update the page
        return jsonify({
            'status': 'success',
            'message': 'Resume processed successfully',
            'tailored_cover_letter': render_template_string(markdown.markdown(tailored_cover_letter)),
        })
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # SELECT the user's resume from users
        resume = (db.execute(
            "SELECT resume FROM users WHERE id = ?;", session["user_id"]
        ))[0]["resume"]
        return render_template("tailored_cover_letter.html", resume=resume)