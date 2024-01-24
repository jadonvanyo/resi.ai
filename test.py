import openai
from bs4 import BeautifulSoup
from helpers import get_tailored_resume

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


def convert_imp_resp_to_html(api_key, text, temp=0.2):
    """Function to call openAI to convert text into an HTML format"""
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


jobdescription = """About the job
Responsibilities

About TikTok USDS
TikTok is the leading destination for short-form mobile video. Our mission is to inspire creativity and bring joy. U.S. Data Security (“USDS”) is a subsidiary of TikTok in the U.S. This new, security-first division was created to bring heightened focus and governance to our data protection policies and content assurance protocols to keep U.S. users safe. Our focus is on providing oversight and protection of the TikTok platform and U.S. user data, so millions of Americans can continue turning to TikTok to learn something new, earn a living, express themselves creatively, or be entertained. The teams within USDS that deliver on this commitment daily span across Trust & Safety, Security & Privacy, Engineering, User & Product Ops, Corporate Functions and more.

Why Join Us
Creation is the core of TikTok's purpose. Our platform is built to help imaginations thrive. This is doubly true of the teams that make TikTok possible.
Together, we inspire creativity and bring joy - a mission we all believe in and aim towards achieving every day. To us, every challenge, no matter how difficult, is an opportunity; to learn, to innovate, and to grow as one team. Status quo? Never. Courage? Always.

At TikTok, we create together and grow together. That's how we drive impact - for ourselves, our company, and the communities we serve.
Join us.

About the Team:
AML (Applied Machine Learning) Platform team combines system engineering and the art of machine learning to develop and run a massively distributed AML system for the United States and all around the world.

On the AML Platform team, you'll have the opportunity to sharpen your expertise in coding, performance analysis, and large-scale systems operation. Join us and you'll have the chance to shape the future of AML systems and make a real, tangible impact on TikTok users.

In order to enhance collaboration and cross-functional partnerships, among other things, at this time, our organization follows a hybrid work schedule that requires employees to work in the office 3 days a week, or as directed by their manager/department. We regularly review our hybrid work model, and the specific requirements may change at any time.

Responsibilities:
Design, build, and maintain highly available, scalable, and fault-tolerant systems.
Update existing AML systems and enhance existing software capabilities.
Ensure that applications are designed with reliability, scalability, and performance in mind.
Monitor and analyze system performance, identifying and resolving issues before causing user impact.
Develop and maintain automated monitoring, alerting, and incident response systems.
Implement and maintain security best practices and ensure compliance with regulatory requirements.
Participate in on-call rotations and respond to issues and incidents within and outside of normal business hours.
Conduct root cause analysis of incidents, hold post-mortem reviews with stakeholders, and implement preventative measures to minimize the risk of similar incidents occurring in the future. 

Qualifications

 Basic:
Expertise in analyzing and troubleshooting Linux-based distributed systems.
Bachelor's/Master's degree in Computer Science, Computer Engineering, or equivalent years of experience in a software engineering role.
Experience programming with at least one commonly used language (C, C++, Python, Go).
Strong understanding of data structures and algorithms.
Competent knowledge of relational database systems.

Preferred:
Ability and experience in designing, developing and maintaining large-scale distributed systems, multi-tenant systems.
Strong understanding of code optimization and routine task automation.
Proficiency in at least one machine learning framework: TensorFlow, PyTorch, MXNet or PaddlePaddle

TikTok is committed to creating an inclusive space where employees are valued for their skills, experiences, and unique perspectives. Our platform connects people from across the globe and so does our workplace. At TikTok, our mission is to inspire creativity and bring joy. To achieve that goal, we are committed to celebrating our diverse voices and to creating an environment that reflects the many communities we reach. We are passionate about this and hope you are too.

TikTok is committed to providing reasonable accommodations in our recruitment processes for candidates with disabilities, pregnancy, sincerely held religious beliefs or other reasons protected by applicable laws. If you need assistance or a reasonable accommodation, please reach out to us at usds.accommodations@tiktokusds.com 
"""

industry = "energy"
company = "Apis Industries"
prevjob = "Quality Engineer"
jobtitle = "Mechanical Engineer"

imp_resp = """The three most important responsibilities in this job description are:
Provide support with quality control, calibration, and debugging: This responsibility is crucial in ensuring that the devices developed by Apis meet the required standards of quality and functionality. The Mechanical Engineer will be responsible for conducting quality checks, calibrating equipment, and troubleshooting any issues that may arise.
Prototype using 3D printers, CNC machines, and laser cutters: As a Mechanical Engineer at Apis, one of the key responsibilities is to create prototypes of new products using advanced manufacturing technologies such as 3D printers, CNC machines, and laser cutters. This involves translating design concepts into physical prototypes for testing and evaluation.
Interact with a complex network of suppliers and manufacturers: In order to successfully design, manufacture, and support the devices developed by Apis, the Mechanical Engineer will need to effectively communicate and collaborate with a network of suppliers and manufacturers. This responsibility involves managing relationships, coordinating production timelines, and ensuring the smooth flow of materials and components for the devices.
These responsibilities are critical in ensuring the successful development, production, and support of Apis' intelligent control systems."""

            
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

# WARNING: Missing API key
tailored_resume_html = get_tailored_resume('', company, imp_resp, industry, jobtitle, prevjob, resume)
print(tailored_resume_html)
print(BeautifulSoup(tailored_resume_html).get_text())