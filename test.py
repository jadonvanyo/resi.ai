import markdown
import re
from cs50 import SQL
import datetime

            
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

differences = """
| Original | Updated |
|------------------------------------------------|------------------------------------------------|
| Adaptable and curious mechanical engineer | Mechanical engineer with a proven track record in leading cross-functional teams, ensuring quality assurance, and implementing engineering solutions in technical environments. |
| managing complex projects | seeking to leverage my mechanical systems expertise and project management skills to contribute to the Facilities Mechanical Engineer role at Intel Corporation, focusing on the maintenance, design, and strategic development of mechanical and HVAC systems to support state-of-the-art semiconductor manufacturing. |
| Technical Program Manager Role at Microsoft | Facilities Mechanical Engineer role at Intel Corporation |
| excited to bring my strong understanding of engineering fundamentals and analytical skills from my technical experience in the aerospace industry. | Seeking to leverage my mechanical systems expertise and project management skills to contribute to the Facilities Mechanical Engineer role at Intel Corporation, focusing on the maintenance, design, and strategic development of mechanical and HVAC systems to support state-of-the-art semiconductor manufacturing. |
| Scrum & Agile Training | Project Management & Strategic Planning |
| Geometric Dimensioning & Tolerancing | Mechanical Systems Analysis & Design |
| Strategic Planning | Project Management & Strategic Planning |
| Remote Team Work | Not mentioned |
| Technical failure analysis reports | Conducted detailed failure analysis, identifying and solving mechanical system issues, contributing to a 22% increase in customer satisfaction and bolstering monthly profits by $750K+. |
| Graduation: May 2021 | Graduation: May 2021 |
| President’s List and Dean’s List (multiple semesters), Honors Scholarship, Kitarich, Peter & Carol, Swagelok Engineering Merit, John T. Pope Memorial, Choose Ohio First | President’s List, Dean’s List, Honors Scholarship, Swagelok Engineering Merit |
"""

imp_resp = """
The three most important responsibilities in this job description are:

1. Ensuring availability, reliability, and maintenance of mechanical and HVAC systems to support manufacturing, clean room, and research and development activities.
2. Designing and analyzing mechanical systems, equipment, and packaging and troubleshooting systematic issues to provide evaluation, recommendations, and solutions to resolve problems.
3. Developing mechanical systems roadmap and asset replacement strategy to ensure reliability, redundancy, and capacity are available for expansion of existing facilities, renovation, and growth."""

# differences_html = markdown.markdown(differences, extensions=['markdown.extensions.tables'])
# differences_html = re.sub(r'<table>', '<table class="table table-striped">', differences_html)
# differences_html = re.sub(r'<th>', '<th scope="col">', differences_html)

# imp_resp_html = markdown.markdown(imp_resp)

# print(imp_resp_html)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///resi.db")

resume_name = 'TEST6'
company = "TEST6"
jobtitle = "TEST6"
tailored_resume = "TEST6"
user_id = 2

# SELECT all saved resumes/cover letters to see if there is more than 4
if db.execute(
    'SELECT COUNT(*) FROM history WHERE user_id = ?;',
    user_id
)[0]['COUNT(*)'] > 4:
    # If more than 4, UPDATE the oldest entry in history database with the newest entry
    db.execute(
        '''UPDATE history 
        SET document_name = ?, company = ?, job_title = ?, document = ?, datetime = ?
        WHERE user_id = ? AND datetime = (SELECT MIN(datetime) FROM history WHERE user_id = ?)
        ''',
        resume_name, 
        company, 
        jobtitle, 
        tailored_resume, 
        datetime.datetime.now(), 
        user_id,
        user_id
    )
# If not past the 5 document limit, just insert the data into history
else:
    db.execute(
        'INSERT INTO history (user_id, document_name, company, job_title, document, datetime) VALUES(?, ?, ?, ?, ?, ?);',
        user_id, resume_name, company, jobtitle, tailored_resume, datetime.datetime.now()
    )
