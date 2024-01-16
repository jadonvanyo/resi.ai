from cryptography.fernet import Fernet
import openai
from flask import redirect, render_template, session
from functools import wraps

def api_key_validation(user_api_key):
    """Check whether a user entered a valid OpenAI API key"""
    # Enter the users entered API key to into an open api
    openai.api_key = f"{user_api_key}"
    
    # Try the user's API key with a test run
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "This is a test. Please respond with 'This is a test.'",
                },
            ],
            max_tokens=5,
            temperature=0,
        )
        
        # If a response exists, the function returns True
        if completion.choices[0].message.content:
            return True
    # If no test message is returned, the model returns false
    except:
        return False
        

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def decrypt_key(encrypted_key, fernet_instance):
    """Decrypt a user's API key"""
    return fernet_instance.decrypt(encrypted_key).decode()

def encrypt_key(key, fernet_instance):
    """Encrypt a user's key prior to storage"""
    return fernet_instance.encrypt(key.encode())

def get_fernet_instance(secret_key):
    """Initialize Fernet using a secret key"""
    return Fernet(secret_key)

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"