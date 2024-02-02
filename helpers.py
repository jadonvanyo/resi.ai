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
            model="gpt-3.5-turbo-1106",
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


def get_imp_resp(api_key, industry, jobdescription, temp=0.5):
    """Generate the 3 most important job responsibilities from OpenAI"""
    # Save the user's OpenAI API Key for use in this function
    openai.api_key = f"{api_key}"

    # Completion for prompt for the 3 most important responsibilities from the job description
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": f"""
            You are an expert resume writer with over 20 years of experience working with job seekers trying to land a role in {industry}.
            """
             },
            {"role": "user", "content": f"""
            Highlight the 3 most important responsibilities in this job description:
            Job Description:
            '''
            {jobdescription}
            '''
            """
             }
        ],
        temperature=temp,
    )

    return completion.choices[0].message.content


def get_differences(api_key, original_resume, tailored_resume, temp=1):
    """Generate a list of the differences between two resumes from OpenAI"""
    # Save the user's OpenAI API Key for use in this function
    openai.api_key = f"{api_key}"

    # Completion for prompt for the differences between the original and tailored resume
    completion = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": f"""
             You are a helpful assistant who's purpose is to list out all of the wording differences between a original and updated resume. You will be provided with an original and updated resume and your task is to list out the differences between wording in the original resume and the updated resume in table format with 2 columns: Original and Updated.
             Be specific and list out exactly what wording was changed.
             """
             },
            {"role": "user", "content": f"""
             Original Resume:
             '''
             {original_resume}
             '''

             Updated Resume:
             '''
             {tailored_resume}
             '''
             """
             }
        ],
        temperature=temp,
        top_p=0.9,
    )

    return completion.choices[0].message.content


def get_tailored_cover_letter_full(api_key, company, jobdescription, jobtitle, prevjob, resume, temp=1):
    """Generate a full tailored cover letter from OpenAI"""
    # Save the user's OpenAI API Key for use in this function
    openai.api_key = f"{api_key}"

    # Completion for prompt for the full tailored cover letter
    completion = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "user", "content": f"""
             You are currently working as a {prevjob} and you're applying for this {jobtitle} at {company}. Based on the job description and resume provided below, please create an amazing cover letter for this job listing that effectively highlights how my background, skills, and experiences make me a perfect fit for this role. The cover letter should be professional, engaging, and tailored to your resume and the job requirements with an emphasis on how you can solve the key challenges that position and the company face.

             Job Description: '''{jobdescription}'''

             Resume: '''{resume}'''
            """
             },
        ],
        temperature=temp,
        top_p=0.75,
    )

    return completion.choices[0].message.content


def get_tailored_cover_letter_partial(api_key, company, jobdescription, jobtitle, prevjob, resume, temp=1):
    """Generate a partial tailored cover letter from OpenAI"""
    # Save the user's OpenAI API Key for use in this function
    openai.api_key = f"{api_key}"

    # Completion for prompt for the partial tailored cover letter
    completion = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "user", "content": f"""
             You are currently working as a {prevjob} and you're applying for this {jobtitle} at {company}. Based on the job description and resume provided below. Please write an amazing cover letter for this job. Please write the cover letter using the format specified below.

            Format:
             '''
             Introduction:
             A Hook: [Write one sentence that uniquely ties your interest or background to the company or industry. For example, a personal connection to the company’s product, mission, or a notable achievement of the company.]

             Why You're Interested in This Role and Company:
             [Write 2-3 sentences about what attracts you to this position and the company. Mention specific aspects of the company’s culture, values, or projects that resonate with you.]

             Summary of Relevant Skills and Experience:
             [Considering the job description, list 2-3 of your skills or experiences that directly align with what the job requires. For each skill/experience, write a brief example that demonstrates how you've effectively used or developed this skill in a previous role or project.]

             Highlighting Achievements:
             [Identify 1-2 key achievements in your career that are particularly relevant to the job. Describe these achievements, quantifying the impact if possible (e.g., increased sales by 20%, reduced process time by 30%).]

             Your Understanding of the Role and Its Challenges:
             [Write 2-3 sentences showing your understanding of what the role entails and any specific challenges it might present, based on the job description or your research on the company.]

             How You Would Add Value:
             [Explain how you would address these challenges or contribute to the role based on your skills and experiences. Be specific about how your unique attributes would benefit the team or company.]

             Closing:
             Reiterate your enthusiasm for the opportunity.
             State your availability for an interview.
             Thank the reader for considering your application.
             '''

             Job Description: '''{jobdescription}'''

             Resume: '''{resume}'''
            """
             },
        ],
        temperature=temp,
        top_p=0.75,
    )

    return completion.choices[0].message.content


def get_tailored_resume(api_key, company, imp_resp, industry, jobdescription, jobtitle, resume, temp=1):
    """Generate a tailored resume from OpenAI"""
    # Save the user's OpenAI API Key for use in this function
    openai.api_key = f"{api_key}"

    # Completion for prompt for the tailored resume
    completion = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": f"""
            You are an expert resume writer with over 20 years of experience working with job seekers trying to land a role in {industry}.
            """
             },
            {"role": "user", "content": f"""
                Highlight the 3 most important responsibilities in this job description:
                Job Description:
                '''
                {jobdescription}
                '''
                """
             },
            {"role": "assistant", "content": f"""
             {imp_resp}
             """
             },
            {"role": "user", "content": f"""
                Based on these 3 responsibilities from the job description, please tailor my resume for this {jobtitle} position at {company}.
                Do not add information from jobs that I did not work at.
                Return only the tailored resume without any additional comments.

                Here's my resume:
                '''
                {resume}
                '''
                """
             },
        ],
        temperature=temp,
        top_p=0.8,
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


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"