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
    openai.api_key = f"{api_key}"
    
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
    openai.api_key = f"{api_key}"
    
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
        temperature = temp,
        top_p=0.9,
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
             You are currently working as a {prevjob} and you're applying for this {jobtitle} at {company}. Based on the job description and resume provided below, please write an amazing cover letter for this job. Please write the cover letter using the following format:

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
        temperature = temp,
        top_p = 0.75,
    )
    
    return completion.choices[0].message.content


def get_tailored_resume(api_key, company, imp_resp, industry, jobdescription, jobtitle, resume, temp=1):
    """Generate a tailored resume from OpenAI"""
    openai.api_key = f"{api_key}"
    
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
        temperature = temp,
        top_p = 0.8,
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
    # Generate the example prompts for the inputs
    price_estimate_inputs = [
        # Prompts for the important responsibilities
        {
            "role": "system", "content": f"""
            You are an expert resume writer with over 20 years of experience working with job seekers trying to land a role in example industry.
            """
        },
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
        # Prompts for the new resume
        {"role": "system", "content": f"""
            You are an expert resume writer with over 20 years of experience working with job seekers trying to land a role in example industry.
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
            Based on the job description provided, the three most important responsibilities for the Engineer-II Stress role in Aerospace Manufacturing are:

            Performing structural analysis to provide analytical definition and ensure structural integrity of components, assemblies, and systems.
            Supporting the review of manufacturing plans and procedures to ensure compliance with design and load requirements.
            Developing and/or utilizing finite element models (global and discrete) and playing an integral role in the workflow release process for structural design.
            """
        },
        {"role": "user", "content": f"""
            Based on these 3 responsibilities from the job description, please tailor my resume for this example job title position at example company. 
            Do not add information from jobs that I did not work at.
            Return only the tailored resume without any additional comments.

            Here's my resume:
            '''
            {resume}
            '''
            """
        },
        # Prompts for the differences between the original and updated resumes
                    {"role": "system", "content": f"""
             You are a helpful assistant who's purpose is to list out all of the wording differences between a original and updated resume. You will be provided with an original and updated resume and your task is to list out the differences between wording in the original resume and the updated resume in table format with 2 columns: Original and Updated. 
             Be specific and list out exactly what wording was changed. 
             """
            },
            {"role": "user", "content": f"""
             Original Resume:
             '''
             {resume}
             '''
             
             Updated Resume:
             '''
             {resume}
             '''
             """
             }
    ]
    
    price_estimate_outputs = [
        # Example return for the important responsibilities
        {
            "role": "assistant",
            "content": """
                Based on the job description provided, the three most important responsibilities for the Engineer-II Stress role in Aerospace Manufacturing are:
                1. Analyze integrated and extensive datasets to extract value, which directly impacts and influences business decisions.
                2. Interpret and analyze data from multiple sources including healthcare provider, member/patient, and third-party data.
                3. Support the design, testing, and implementation of process enhancements and identify opportunities for automation.""",
        },
        # Example return for the tailored resume should be similar to their resume
        {
            "role": "assistant",
            "content": resume,
        },
        # Example return markdown for the differences table
        {
            "role": "assistant",
            "content": """EXAMPLE:
            | Original                                                                                          | Updated                                                                                                                                                  |
            |---------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
            | Summary: Adaptable and curious mechanical engineer                                                | Summary: Detail-oriented Stress Engineer                                                                                                                 |
            | seeking to apply my skills to the Technical Program Manager Role at Microsoft.                     | with a solid foundation in mechanical engineering principles and extensive experience                                                                     |
            | I am excited to bring my strong understanding of engineering fundamentals                         | in structural analysis and cross-functional project management within the aerospace industry.                                                             |
            | and analytical skills from my technical experience in the aerospace industry.                      | Proven track record of improving component integrity, optimizing manufacturing processes,                                                                 |
            |                                                                                                   | and ensuring compliance with rigorous industry standards.                                                                                                 |
            |                                                                                                   | Adept at utilizing advanced analysis software and methodologies                                                                                          |
            |                                                                                                   | to support design, manufacturing, and testing of aerospace structures.                                                                                   |
            | Microsoft Office Suite                                                                                          | - Microsoft Office Suite                                                                                                                                 |
            | Cross-Functional Team Work                                                                              | - Cross-Functional Team Collaboration                                                                                                                    |
            | Scrum & Agile Training                                                                                          | - Scrum & Agile Methodologies                                                                                                                            |
            |                                                                                                   | - Structural Analysis                                                                                                                                    |
            |                                                                                                   | - Finite Element Modeling (FEM)                                                                                                                          |
            | Component Repair Technologies | Quality Engineer | Accomplished a 100% reduction in bushing-related warranties | - Reduced bushing-related warranties by 100% through cross-functional team leadership |
            | by leading a cross-functional team of 5 to enhance work instructions, tooling, and training      | and enhanced work instructions, positively impacting annual savings by over $115K.                                                                      |
            | for bore bushing installation, resulting in annual savings exceeding $115K                        |                                                                                                                                                          |
            | Assessed risk factors and quality assurance for 100+ repaired parts                               | - Performed structural integrity assessments for 100+ aerospace components                                                                               |
            | to ensure they met the technical and safety requirements, resulting in a contribution of $750K+ to monthly profits  | ensuring compliance with technical and safety standards, contributing to monthly profits of $750K+.|
            | Achieved a 100% success rate in containing and preventing potential warranty issues               | - Led 25+ failure investigations to improve internal processes,                                                                                         |
            | by leading 25+ investigations to enhance internal processes, resulting in a 22% increase in customer satisfaction | achieving a 100% success rate in containing potential issues and increasing customer satisfaction by 22%. |
            | Developed and delivered technical failure analysis reports that determine root cause failure      | - Developed and delivered comprehensive technical failure analysis reports                                                                               |
            | and work with internal and external stakeholders implementing containment, corrective, and preventative actions to remedy the root cause | to internal and external stakeholders, facilitating the implementation of corrective actions.  |
            | Collaborated with different subteams to design and manufacture sUAVs, terrain mapping payloads,   | - Collaborated on the design and manufacture of aerospace recovery systems,                                                                              |
            | and recovery systems                                                                              | contributing to the structural and operational integrity of small unmanned aerial vehicles (sUAVs) and payloads. |
            | Led team to innovate and design new mechanical carbon dioxide ejection system for ejections at 20000 ft | - Innovated a new mechanical CO2 ejection system for high-altitude applications,                                                                         |
            |                                                                                                   | demonstrating proficiency in design and analysis for aerospace applications.                                                                             |
            | Preformed testing to ensure designs meet stress, tolerance, and failure requirements throughout their lifecycle | - Conducted stress analysis and tolerance testing throughout product lifecycle,                                                                           |
            | Designed and implemented testing equipment that increased cycle durability testing capacity by 33% | ensuring design robustness and compliance with engineering standards.                                                                                     |
            | Established a storage system that optimized storage process and increased capacity by 25%         |                                                                                                                                                          |
            | Bachelor of Science in Mechanical Engineering, Grade Point Average: 3.990/4.000                   | Bachelor of Science in Mechanical Engineering, GPA: 3.990/4.000                                                                                          |
            | Technical Courses: Tech Start-ups: Product Market Fit, Concepts of Design, Technical Report Writing | Relevant Coursework: Concepts of Design, Technical Report Writing                                                                                        |
            | Awards: President’s List and Dean’s List (multiple semesters), Honors Scholarship, Kitarich, Peter & Carol, Swagelok Engineering Merit, John T. Pope Memorial, Choose Ohio First | - President’s List and Dean’s List (multiple semesters)                                                                                                  |
            |                                                                                                   | - Various Engineering and Merit Scholarships                                                                                                             |
            | Real Estate Investment and Management | Investor and Manager                                      | (The section on Real Estate Investment and Management has been removed)                                                                                  |
            | Panda Express | Counter Help/Cook                                                                 | (The section on Panda Express experience has been removed)   
            """,
        },
    ]
    
    return price_estimate_inputs, price_estimate_outputs


def price_estimation(user_api_key, price_estimate_inputs, price_estimate_outputs):
    """Estimate the total price of the call to ChatGPT"""
    # Enter the users entered API key to into an open api
    openai.api_key = f"{user_api_key}"
    
    # Count tokens for the inputs
    inputs = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=price_estimate_inputs,
        temperature=1,
        max_tokens=1,  # we're only counting input tokens here, so let's not waste tokens on the output
    )
    
    # Count tokens for the outputs
    outputs = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=price_estimate_outputs,
        temperature=1,
        max_tokens=1,  # we're only counting input tokens here, so let's not waste tokens on the output
    )
    
    # Calculate the total price to tailor the resume
    total_cost = (((inputs.usage.prompt_tokens)* 0.01) + ((outputs.usage.prompt_tokens) * 0.03)) / 1000

    return total_cost


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"