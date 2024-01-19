import openai

def get_response(api_key, prompt, temp=0):
    """Generate a response from ChatGPT"""
    # Enter the users entered API key to into an open api
    openai.api_key = f"{api_key}"
    
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=temp,
    )
    
    return completion.choices[0]

jobdescription = """You could be the one who changes everything for our 28 million members. Centene is transforming the health of our communities, one person at a time. As a diversified, national organization, you’ll have access to competitive benefits including a fresh perspective on workplace flexibility.
Position Purpose: Analyze integrated and extensive datasets to extract value, which directly impacts and influences business decisions. Work collaboratively with key business stakeholders to identify areas of value, develop solutions, and deliver insights to reduce overall cost of care for members and improve their clinical outcomes.
Interpret and analyze data from multiple sources including healthcare provider, member/patient, and third-party data.
Support execution of large-scale projects with limited direction from leadership
Identify and perform root-cause analysis of data irregularities and present findings and proposed solutions to leadership and/or customers
Manage multiple, variable tasks and data review processes with limited supervision within targeted timelines
Support the design, testing, and implementation of process enhancements and identify opportunities for automation
Apply expertise in quantitative analysis, data mining, and the presentation of data to see beyond the numbers and understand how customers interact with analytic products
Support multiple functions and levels of the organization and effectively, both verbally and visually, communicate findings and insights to non-technical business partners
Independently engage with customers and business partners to gather requirements and validate results
Communicate and present data-driven insights and recommendations to both internal and external stakeholders, soliciting and incorporating feedback when required
Education/Experience: Bachelor’s degree in business, economics, statistics, mathematics, actuarial science, public health, health informatics, healthcare administration, finance or related field or equivalent experience. 2+ years of experience working with large databases, data verification, and data management, or 1+ years IT experience. Healthcare analytics experience preferred. Working knowledge of SQL/query languages. Preferred knowledge of programmatic coding languages such as Python and R. Knowledge of statistical, analytical, or data mining techniques including basic data modeling, trend analysis, and root-cause analysis preferred. Preferred knowledge of modern business intelligence and visualization tools including Microsoft PowerBI.

Regional and HBR Analytics: Experience in emerging trend analysis, financial modeling, claims pricing, contract/network analysis, and/or ROI evaluation preferred. Familiarity with claims payment, utilization management, provider/vendor contracts, risk adjustment for government sponsored healthcare desired.
"""

prompt = f"""
            You are an expert resume writer with over 20 years of experience working with
            job seekers trying to land a role in industry.
            Highlight the 3 most important responsibilities in this job description:
            Job Description:
            '''
            {jobdescription}
            '''
            """
            
resume = """Summary: Adaptable and curious mechanical engineer with experience managing complex projects, working on cross-functional teams, and problem solving seeking to apply my skills to the Technical Program Manager Role at Microsoft. I am excited to bring my strong understanding of engineering fundamentals and analytical skills from my technical experience in the aerospace industry.   

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
"""
            
example_inputs = [
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
example_outputs = [
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

# Enter the users entered API key to into an open api
# openai.api_key = 

# Count token function
inputs = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=example_inputs,
    temperature=0.2,
    max_tokens=1,  # we're only counting input tokens here, so let's not waste tokens on the output
)

outputs = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=example_outputs,
    temperature=0.2,
    max_tokens=1,  # we're only counting input tokens here, so let's not waste tokens on the output
)
total_cost = (((inputs.usage.prompt_tokens) / 1000) * 0.001) + (((outputs.usage.prompt_tokens) / 1000) * 0.002)
print(total_cost)