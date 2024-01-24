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
             You are a helpful assistant who's purpose is to list out all of the wording differences between a original and updated resume. You will be provided with an original and updated resume and your task is to list out the differences between the original resume and the updated resume in table format with 2 columns: Original and Updated. Be specific and list out exactly what wording was changed. Styling differences can be ignored. Return the table in HTML that can easily be added into the inner HTML of a website. Only return the code, nothing else.
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
    


def get_tailored_resume(api_key, company, imp_resp, industry, jobtitle, prevjob, resume, temp=0.5):
    """Generate a tailored resume from OpenAI"""
    openai.api_key = f"{api_key}"
    
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"""
            You are an expert resume writer with over 20 years of experience working with job seekers trying to land new roles at their dream companies. You specialize in helping write resumes for people looking to transition to a new career path.

            You will be provided with a client's target company, target job title, target job industry, top 3 job responsibilities at that target job, their resume, and their previous job title. Based on this information, please tailor the client's resume for their target job. Return the tailored resume in HTML that can easily be added into the inner HTML of a website. Only return the code, nothing else. Do not make information up."""
            },
            {"role": "user", "content": """
                Target Company: Apis Innovation
                Target Job Title: Mechanical Engineer
                Target Job Industry: Energy
                Previous Job Title: Quality Engineer
                Top 3 Job Responsibilities:
                '''
                The three most important responsibilities in this job description are:
                Provide support with quality control, calibration, and debugging: This responsibility is crucial in ensuring that the devices developed by Apis meet the required standards of quality and functionality. The Mechanical Engineer will be responsible for conducting quality checks, calibrating equipment, and troubleshooting any issues that may arise.
                Prototype using 3D printers, CNC machines, and laser cutters: As a Mechanical Engineer at Apis, one of the key responsibilities is to create prototypes of new products using advanced manufacturing technologies such as 3D printers, CNC machines, and laser cutters. This involves translating design concepts into physical prototypes for testing and evaluation.
                Interact with a complex network of suppliers and manufacturers: In order to successfully design, manufacture, and support the devices developed by Apis, the Mechanical Engineer will need to effectively communicate and collaborate with a network of suppliers and manufacturers. This responsibility involves managing relationships, coordinating production timelines, and ensuring the smooth flow of materials and components for the devices.
                These responsibilities are critical in ensuring the successful development, production, and support of Apis' intelligent control systems.
                '''

                My Resume:
                '''
                Summary: Adaptable and curious mechanical engineer with experience managing complex projects, working on cross-functional teams, and problem solving seeking to apply my skills to the Technical Program Manager Role at Microsoft. I am excited to bring my strong understanding of engineering fundamentals and analytical skills from my technical experience in the aerospace industry.   

                Key Skills:
                Microsoft Office Suite			 Cross-Functional Team Work		          Python
                Scrum & Agile Training			 Geometric Dimensioning & Tolerancing	          MATLAB/Simulink
                Strategic Planning			 Failure Analysis	                       		          SolidWorks
                Technical Report Writing		 	 Remote Team Work			          Soldering

                Technical Experience:
                Component Repair Technologies | Mentor, OH | Quality Engineer | June 2021-June 2023
                Accomplished a 100% reduction in bushing-related warranties by leading a cross-functional team of 5 to enhance work instructions, tooling, and training for bore bushing installation, resulting in annual savings exceeding $115K
                Assessed risk factors and quality assurance for 100+ repaired parts to ensure they met the technical and safety requirements, resulting in a contribution of  $750K+ to monthly profits
                Achieved a 100% success rate in containing and preventing potential warranty issues by leading 25+ investigations to enhance internal processes, resulting in a 22% increase in customer satisfaction
                Developed and delivered technical failure analysis reports that determine root cause failure and work with internal and external stakeholders implementing containment, corrective, and preventative actions to remedy the root cause
                The University of Akron Rocket Design Team | Akron, OH |  Recovery Team Lead & Payload Team Member  | Aug 2018-May 2021
                Collaborated with different subteams to design and manufacture sUAVs, terrain mapping payloads, and recovery systems 
                Presented new design ideas to senior classmates and alumni to raise additional funding for the rocket team
                Led a team of 5 individuals to generate concepts, prototype, demonstrate & test a guided recovery system
                Led team to innovate and design new mechanical carbon dioxide ejection system for ejections at 20000 ft
                Bendix Commercial Vehicle Systems LLC | Elyria, OH | Air Treatment Engineering Co-op | May 2020-August 2020 
                Worked on a cross-functional remote Scrum team researching and analyzing different trailer system variations to test and determine whether an auto trailer park release feature could be integrated into North American models
                Collaborated with a product design team to analyze and test different covers for an air treatment product
                Bendix Commercial Vehicle Systems LLC | Elyria, OH | Actuators Engineering Co-op | Sept 2019-Jan 2020 
                Preformed testing to ensure designs meet stress, tolerance, and failure requirements throughout their lifecycle
                Designed and implemented testing equipment that increased cycle durability testing capacity by 33%
                Established a storage system that optimized storage process and increased capacity by 25%
                Designed and analyzed new actuator clamp band design geometries in Creo Parametric to improve the overall sealing by 8%

                Education: 
                The University of Akron, Akron OH				           		 		    Graduation: May 2021
                Bachelor of Science in Mechanical Engineering, Grade Point Average: 3.990/4.000, Williams Honors College Scholar
                Technical Courses: Tech Start-ups: Product Market Fit, Concepts of Design, Technical Report Writing
                Awards: President’s List and Dean’s List (multiple semesters), Honors Scholarship, Kitarich, Peter & Carol, Swagelok Engineering Merit, John T. Pope Memorial, Choose Ohio First

                Other Experience:
                Real Estate Investment and Management | Cleveland, OH | Jul 2022-Present | Investor and Manager 
                Find, analyze, negotiate, fund, rehab, and manage 5 real estate investment properties in the greater Cleveland area
                Panda Express | Cuyahoga Falls, OH | Aug 2017-May 2021 | Counter Help/Cook 
                Delighted customers, served, prepared, and cooked food, ran cash registers, cleaned, and raised $1000+ for local charities
                '''
                """
            },
            {"role": "assistant", "content": """
                <div>
                    <h2>Summary</h2>
                    <p>Detail-oriented Quality Engineer with a strong background in quality engineering and project management, seeking the Mechanical Engineer role at Apis Industries. Brings extensive experience in quality control, calibration, and debugging, coupled with a deep understanding of engineering principles and advanced manufacturing technologies.</p>
                    
                    <h2>Key Skills</h2>
                    <ul>
                        <li>Quality Control and Assurance</li>
                        <li>Calibration and Debugging</li>
                        <li>Prototyping (3D Printing, CNC Machining, Laser Cutting)</li>
                        <li>Supplier and Manufacturer Interaction</li>
                        <li>Cross-Functional Teamwork</li>
                        <li>Strategic Planning and Project Management</li>
                        <li>Technical Report Writing</li>
                        <li>CAD Tools (SolidWorks, Creo Parametric)</li>
                        <li>Python, MATLAB/Simulink</li>
                        <li>Microsoft Office Suite</li>
                        <li>Scrum & Agile Methodologies</li>
                    </ul>

                    <h2>Technical Experience</h2>
                    <h3>Component Repair Technologies | Mentor, OH</h3>
                    <p><strong>Quality Engineer | June 2021-June 2023</strong></p>
                    <ul>
                        <li>Led a cross-functional team to enhance work instructions, tooling, and training for bore bushing installation, resulting in a 100% reduction in bushing-related warranties and annual savings exceeding $115K.</li>
                        <li>Assessed risk factors and conducted quality assurance for over 100 repaired parts, contributing $750K+ to monthly profits.</li>
                        <li>Led 25+ investigations to enhance internal processes, achieving a 100% success rate in containing and preventing potential warranty issues and increasing customer satisfaction by 22%.</li>
                        <li>Developed and delivered technical failure analysis reports, collaborating with stakeholders to implement containment, corrective, and preventative actions.</li>
                    </ul>

                    <h3>The University of Akron Rocket Design Team | Akron, OH</h3>
                    <p><strong>Recovery Team Lead & Payload Team Member | Aug 2018-May 2021</strong></p>
                    <ul>
                        <li>Collaborated with different subteams to design and manufacture small unmanned aerial vehicles (sUAVs), terrain mapping payloads, and recovery systems.</li>
                        <li>Presented new design ideas to senior classmates and alumni, raising additional funding for the rocket team.</li>
                        <li>Led a team of 5 individuals to generate concepts, prototype, demonstrate, and test a guided recovery system.</li>
                        <li>Innovated and designed a mechanical carbon dioxide ejection system for ejections at 20,000 ft.</li>
                    </ul>

                    <h3>Bendix Commercial Vehicle Systems LLC | Elyria, OH</h3>
                    <p><strong>Air Treatment Engineering Co-op | May 2020-Aug 2020</strong></p>
                    <ul>
                        <li>Worked on a cross-functional remote Scrum team to research and analyze different trailer system variations for North American models.</li>
                        <li>Collaborated with a product design team to analyze and test different covers for an air treatment product.</li>
                    </ul>

                    <h3>Bendix Commercial Vehicle Systems LLC | Elyria, OH</h3>
                    <p><strong>Actuators Engineering Co-op | Sept 2019-Jan 2020</strong></p>
                    <ul>
                        <li>Conducted testing to ensure designs meet stress, tolerance, and failure requirements throughout their lifecycle.</li>
                        <li>Designed and implemented testing equipment, increasing cycle durability testing capacity by 33%.</li>
                        <li>Established a storage system that optimized storage processes and increased capacity by 25%.</li>
                        <li>Designed and analyzed new actuator clamp band design geometries in Creo Parametric, improving overall sealing by 8%.</li>
                    </ul>

                    <h2>Education</h2>
                    <p>The University of Akron, Akron, OH<br>
                    Bachelor of Science in Mechanical Engineering, GPA: 3.990/4.000, May 2021<br>
                    Relevant Courses: Technical Report Writing, Geometric Dimensioning & Tolerancing<br>
                    Awards: President’s List, Dean’s List</p>

                    <h2>Other Experience</h2>
                    <h3>Real Estate Investment and Management | Cleveland, OH | Jul 2022-Present</h3>
                    <p><strong>Investor and Manager</strong></p>
                    <ul>
                        <li>Managed the entire lifecycle of real estate investment properties, demonstrating project management and strategic planning skills.</li>
                    </ul>

                    <h3>Panda Express | Cuyahoga Falls, OH | Aug 2017-May 2021</h3>
                    <p><strong>Counter Help/Cook</strong></p>
                    <ul>
                        <li>Provided excellent customer service and collaborated effectively within a team environment.</li>
                    </ul>
                </div>
                """
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