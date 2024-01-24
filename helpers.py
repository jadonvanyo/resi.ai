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


def convert_imp_resp_to_html(api_key, text, temp=0.2):
    """Function to call openAI to convert important responsibilities into an HTML format"""
    openai.api_key = f"{api_key}"
    
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful frontend programming assistant. You will take user input text and convert it to HTML that can easily be added into the inner HTML of a website. Only return the code, nothing else."},
            {"role": "user", "content": """Based on the job description for a healthcare analytics position, the three most important responsibilities are: 
             Analyze and Interpret Data: This role involves analyzing and interpreting data from multiple sources, including healthcare providers, members/patients, and third-party data. The ability to extract valuable insights from extensive datasets is a crucial responsibility. 
             Support Large-Scale Projects: The position requires supporting the execution of large-scale projects with limited direction from leadership. This includes managing multiple tasks and data review processes within targeted timelines, as well as identifying opportunities for process enhancements and automation.
             Communicate Data-Driven Insights: Effective communication of data-driven insights and recommendations is vital. The job involves presenting findings and insights to both internal and external stakeholders, including non-technical business partners. This includes engaging with customers and business partners to gather requirements and validate results."""
            },
            {"role": "assistant", "content": """
             <div>
              <h2>Based on the job description for a healthcare analytics position, the three most important responsibilities are:</h2>
              <ol>
                <li>
                    <strong>Analyze and Interpret Data:</strong> This role involves analyzing and interpreting data from multiple sources, including healthcare providers, members/patients, and third-party data. The ability to extract valuable insights from extensive datasets is a crucial responsibility.
                </li>
                <li>
                    <strong>Support Large-Scale Projects:</strong> The position requires supporting the execution of large-scale projects with limited direction from leadership. This includes managing multiple tasks and data review processes within targeted timelines, as well as identifying opportunities for process enhancements and automation.
                </li>
                <li>
                    <strong>Communicate Data-Driven Insights:</strong> Effective communication of data-driven insights and recommendations is vital. The job involves presenting findings and insights to both internal and external stakeholders, including non-technical business partners. This includes engaging with customers and business partners to gather requirements and validate results.
                </li>
              </ol>
             </div>"""
            },
            {"role": "user", "content": text},
        ],
        temperature=temp,
    )
    
    return completion.choices[0].message.content


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
    openai.api_key = f"{api_key}"
    
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"""
            You are an expert resume writer with over 20 years of experience working with job seekers trying to land a role in {industry}.
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


def get_differences(api_key, original_resume, tailored_resume, temp=0.2):
    """Generate a list of the differences between two resumes from OpenAI"""
    openai.api_key = f"{api_key}"
    
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"""
             You are a helpful assistant who's purpose is to list out all of the wording differences between a original and updated resume. You will be provided with an original and updated resume and your task is to list out the differences between the original resume and the updated resume in table format with 2 columns: Original and Updated. Be specific and list out exactly what wording was changed. Only list a sentence if it has been changed. 
             
             Return the table in HTML that can easily be added into the inner HTML of a website. Only return the code, nothing else.
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
        temperature = temp,
    )
    
    return completion.choices[0].message.content
    

def get_tailored_resume(api_key, company, imp_resp, industry, jobtitle, prevjob, resume, temp=0.7):
    """Generate a tailored resume from OpenAI"""
    openai.api_key = f"{api_key}"
    
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"""
            You are an expert resume writer with over 20 years of experience working with job seekers trying to land new roles at their dream companies. You specialize in helping write resumes for people looking to transition to a new career path.

            You will be provided with a client's target company, target job title, target job industry, top 3 job responsibilities at that target job, their resume, and their previous job title. Based on top 3 job responsibilities, please tailor the client's resume for their target job. Only adjust the client's resume wording, do not add additional information.
            
            Return the tailored resume in HTML that can easily be added into the inner HTML of a website. Only return the code, in the following format:
            <div>
                "Tailored Resume Here"
            </div>"""
            },
            {"role": "user", "content": f"""
                Target Company: {company}
                Target Job Title: {jobtitle}
                Target Job Industry: {industry}
                Previous Job Title: {prevjob}
                Top 3 Job Responsibilities:
                '''
                {imp_resp}
                '''
                My Resume:
                '''
                {resume}
                '''
                """
            }
        ],
        temperature = temp,
    )
    
    return completion.choices[0].message.content


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