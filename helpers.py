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

def get_fernet_instance():
    """Initialize and return a Fernet instance using a secret key"""
    # TODO: Create your own secret key and update the file path to the file with the secret key
    # Open the file containing the secret key
    with open('/Users/jadonvanyo/Desktop/cs50/final_project/secret_keys/secret_key.txt', 'r', encoding='utf-8') as file:
        # Generate fernet instance to encrypt the user's secret key from secret key in file
        fernet_instance = Fernet(file.read().strip())
    
    return fernet_instance

def get_response(api_key, prompt, temp=0):
    """Generate a response from ChatGPT"""
    # Enter the users entered API key to into an open api
    openai.api_key = f"{api_key}"
    
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=temp,
    )
    
    return completion.choices[0].message.content

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

def price_estimator_prompts(jobdescription, resume):
    """Generate example input and output messages for the price estimation"""
    price_estimate_inputs = [
        {
            "role": "user",
            "content": f"""
                You are an expert resume writer with over 20 years of experience working with
                job seekers trying to land a role in industry.
                Highlight the 3 most important responsibilities in this job description:
                Job Description:
                '''
                {jobdescription}
                '''
                """,
        },
        {
            "role": "user",
            "content": f"""
                You are an expert resume writer with over 20 years of experience working with
                job seekers trying to land a role in industry. You specialize in helping
                write resumes for a example job looking to transition to a new career path 
                in industry.

                Based on these 3 most important responsibilities from the job description,
                please tailor my resume for this example job title position at
                example company. Do not make information up.

                3 Most important responsibilities: 
                '''
                Example:
                1. Analyze integrated and extensive datasets to extract value, which directly impacts and influences business decisions.
                2. Interpret and analyze data from multiple sources including healthcare provider, member/patient, and third-party data.
                3. Support the design, testing, and implementation of process enhancements and identify opportunities for automation.
                '''

                Resume:
                '''
                {resume}
                '''
                """,
        },
        {
            "role": "user",
            "content": f"""
                List out the differences between my original resume and the suggested draft \
                in table format with 2 columns: Original and Updated. Be specific and list out \
                exactly what was changed, down to the exact wording.

                My Original:
                '''
                {resume}
                '''

                Suggested Draft:
                '''
                {resume}
                '''
                """,
        },
    ]
    
    price_estimate_outputs = [
        {
            "role": "assistant",
            "content": """
                Example:
                1. Analyze integrated and extensive datasets to extract value, which directly impacts and influences business decisions.
                2. Interpret and analyze data from multiple sources including healthcare provider, member/patient, and third-party data.
                3. Support the design, testing, and implementation of process enhancements and identify opportunities for automation.""",
        },
        {
            "role": "assistant",
            "content": resume,
        },
        {
            "role": "assistant",
            "content": resume,
        },
    ]
    
    return price_estimate_inputs, price_estimate_outputs

def price_estimation(user_api_key, price_estimate_inputs, price_estimate_outputs):
    """Estimate the total price of the call to ChatGPT"""
    # Enter the users entered API key to into an open api
    openai.api_key = f"{user_api_key}"
    
    # Count tokens for the inputs
    inputs = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=price_estimate_inputs,
        temperature=0.2,
        max_tokens=1,  # we're only counting input tokens here, so let's not waste tokens on the output
    )
    
    # Count tokens for the outputs
    outputs = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=price_estimate_outputs,
        temperature=0.2,
        max_tokens=1,  # we're only counting input tokens here, so let's not waste tokens on the output
    )
    
    # Calculate the total price to tailor the resume
    total_cost = (((inputs.usage.prompt_tokens) / 1000) * 0.001) + (((outputs.usage.prompt_tokens) / 1000) * 0.002)

    return total_cost


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"