import openai

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
        # TODO: Try doubling the resume?? (Eliminate this feature, just do a cover letter feature)
        {
            "role": "assistant",
            "content": f'{resume}',
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

    return total_cost, inputs.usage.prompt_tokens, outputs.usage.prompt_tokens

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
    
    return completion.choices[0].message.content, completion.usage.prompt_tokens

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
    
    return completion.choices[0].message.content,  completion.usage.prompt_tokens

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
    
    return completion.choices[0].message.content, completion.usage.prompt_tokens

job = """
About Remedy Robotics
Cardiovascular disease is the #1 cause of morbidity and mortality in the world. Much of this could be prevented with better access to specialist care. Take stroke as an example: any delay in treatment can lead to permanent disability or death. However, due to a lack of specialist surgeons, the most effective intervention can only be performed in 2% of US hospitals. For patients who present to one of the 98% of hospitals that do not offer the surgery, treatment is either significantly delayed or not offered at all because timely transfer is not feasible.

Our mission is to bring state-of-the-art vascular intervention to anyone, anytime, regardless of their location. Our team of medical clinicians, roboticists, and machine learning experts are working to bridge this gap by building the world’s first remotely-operated, semi-autonomous endovascular surgical robot.

We’ve already done what nobody else could—using our system, doctors from around the world were able to remotely perform this procedure from as far as 8,000 miles away. We now need your help to bring this technology out of the laboratory and into hospitals everywhere.


The Role
We’re looking for a motivated, senior mechanical engineer to design key components of a novel, life saving surgical robot.


You Will
Design mechanisms for a surgical robot and surgical tools.
Participate in the entire design cycle, including the development of conceptual and detailed designs for prototypes, pilot machines, and production machines.
Generate specifications, component drawings, assembly drawings, and interface control documents.
Participate in subsystem level testing including the development and execution of testing plans as well as data collection and analysis.
Leverage experience and engineering judgement to rapidly design and produce proof of concept hardware for fast-moving research and development projects.


You Have
5+ years of industry experience.
Recent experience designing electromechanical mechanisms.
Strong mechanical design, integration and mechanism analysis skills using 3D modeling (e.g., SolidWorks, OnShape)
Ability to work with hand tools and prototyping equipment.
The ability to communicate complex ideas clearly and concisely.
"""

resume = """
Summary: Adaptable and curious mechanical engineer with experience managing complex projects, working on cross-functional teams, and problem solving seeking to apply my skills to the Technical Program Manager Role at Microsoft. I am excited to bring my strong understanding of engineering fundamentals and analytical skills from my technical experience in the aerospace industry.   

Key Skills:
Microsoft Office Suite			 
Cross-Functional Team Work		          
Python
Scrum & Agile Training			 
Geometric Dimensioning & Tolerancing	          
MATLAB/Simulink
Strategic Planning			 
Failure Analysis	                       		          
SolidWorks
Technical Report Writing		 	 
Remote Team Work			          
Soldering

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
"""

api_key = ''
industry = 'robotics'
company = 'Remedy Robotics'
title = 'Senior Mechanical Engineer'
prevjob = 'Quality Engineer'

# Call function to create the example prompts required a tailor the resume
price_estimate_inputs, price_estimate_outputs = price_estimator_prompts(job, resume)

print(price_estimation(api_key,price_estimate_inputs, price_estimate_outputs))

# # API call to get the 3 most important responsibilities from the description
# imp_resp, imp_resp_tokens = get_imp_resp(api_key, industry, job)

# # API call to get tailored resume from user information
# tailored_resume, tailored_resume_tokens = get_tailored_resume(api_key, company,imp_resp, industry, job, title, resume)

# # API call to get the differences comparison between old and new resumes
# differences, differences_tokens = get_differences(api_key, resume, tailored_resume)

# print(imp_resp_tokens)
# print(tailored_resume_tokens)
# print(differences_tokens)

# (0.09575999999999998, 3753, 1941)
# 96
# 832
# 1013
# (0.17, ???, 3481)
# 485
# 1464
# 1532

tailor_cover_letter_prompt = f"""
    You are currently working as a {prevjob} and you're applying for this {title} at {company}. Based on the job description and resume provided below, please write an amazing cover letter for this job. Please write the cover letter using the following format:

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

    Job Description: '''{job}'''

    Resume: '''{resume}'''
"""