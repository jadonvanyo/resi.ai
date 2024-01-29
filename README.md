# Resi.ai
#### Video Demo:  <URL HERE>
## Description:
### Problem:
Applying for jobs has gotten noticeably more difficult over the past few years. More companies are using advanced AI technologies to quickly screen candidates for potential job openings, and job boards like Indeed and LinkedIn make it trivially easy to post a new job opening to thousands of people in seconds. Applying for a job now feels like a question of quantity rather than quality.

### Solution:
This web application aims to give some of the power back to the job seekers by providing them with an easy to use tool to quickly create quality resumes customized to the job description leveraging the power of AI. All they will need is a working OpenAI API Key, an existing resume, and the job description. All of the prompting is handled by this program, so it is as easy as copying and pasting a resume and job description.

### Pages:

#### Account:


#### Tailored Resumes:
This page gives the user all the fields that are required to create an expert resume writer to tailor their resume to their target job description. The user just needs to enter their target job title, target industry, target company, target job description, and an existing resume. When the user selects the "Submit Resume" button, the website uses **A**synchronous **J**avaScript **A**nd **X**ML (**AJAX**) to update the web page to show a loading indicator and send a request for the index function from the Flask backend. The Flask backend will determine whether to return an error or use OpenAI's API to return the 3 most important resonsibilites of the job, a tailored resume, and a list of all the differences between the two and the page is dynamically updated again with all the information using JavaScript.

## File Breakdown:
### app.py:
### helper.py: