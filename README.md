# Resi.ai
#### Video Demo:  <URL HERE>
## Description:
### Problem:
Applying for jobs has gotten noticeably more difficult over the past few years. More companies are using advanced AI technologies to quickly screen candidates for potential job openings, and job boards like Indeed and LinkedIn make it trivially easy to post a new job opening to thousands of people in seconds. Applying for a job now feels like a question of quantity rather than quality.

### Solution:
This web application aims to give some of the power back to the job seekers by providing them with an easy to use tool to quickly create quality resumes customized to the job description leveraging the power of AI. All they will need is a working OpenAI API Key, an existing resume, and the job description. All of the prompting is handled by this program, so it is as easy as copying and pasting a resume and job description.

### Pages:

#### Account:
This page allows the user to update their email, password, OpenAI API key, and resume. Once saved in the database, the resume will autofill into any felids that require a resume to improve user experience. When the user clicks the update button, the website uses **A**synchronous **J**avaScript **A**nd **X**ML (**AJAX**) to send a request for the account function from the Flask backend. The Flask backend will determine whether to return an error or update the user's information in the resi.db database using SQLite, and dynamically update the webpage using AJAX to display an alert message below the submit button showing what was wrong or what was updated. The user's password will be hashed and OpenAI API Key will be encrypted for security any time they are updated on this page.

#### Enter API:
This is the page the user is redirected to after registering for the first time. The webpage will give the user a explanation on how to set up their OpenAI API key and at the bottom of the page, it provides the user an input box to enter the API key they have generated. If the user clicks the "Enter API Key" button, the website will send a request for the api_key function from the Flask backend. The Flask backend will determine whether to return an error or encrypt and update the user's OpenAI API Key in the resi.db database with the encrypted key, and dynamically update the webpage using AJAX to display an alert message below the submit button showing what was wrong or that the API Key was successfully updated. The user can update their API Key at any time from this page.

#### Price Estimator:
This feature allows the user to estimate how much a particular tailored resume will cost them. This page gives the user a text box to enter the job description and their resume (if they have already entered the resume in the Account, this will autofill). When the user clicks the "Get Price Estimate" button, the Flask backend will fill in the resume and job description to an example template of roughly what it would expect the input and output prompts to be and use OpenAI's API to count the number of tokens used. It then multiplies the number of tokens of the output and input by the current market rate, and renders a new template for the user displaying the expected price. The API call to count the tokens will only cost one token itself, making it a trivial cost.

#### Tailored Resumes:
This is the main feature of this web application. This page gives the user all the fields that are required to create an expert resume writer to tailor their resume to their target job description. The user just needs to enter their target job title, target industry, target company, target job description, and an existing resume. When the user selects the "Submit Resume" button, the website uses AJAX to update the web page to show a loading indicator and send a request for the index function from the Flask backend. The Flask backend will determine whether to return an error or use OpenAI's API to return the 3 most important responsibilities of the job, a tailored resume, and a list of all the differences between the two and the page is dynamically updated again with all the information using JavaScript.

#### History:
This feature allows the user to view the last 5 documents that they have generated. The documents are pulled from the history table in the resi.db database and displayed in a collapsible accordion for easy viewing. The oldest document in the history is replaced whenever the user generates a new document in the index function. The old documents are displayed from newest to oldest and include the target job title, target company, document type, and when it was generated.

## File Breakdown:
### app.py:
This file contains all the necessary routes for the web application: index, about, account, api_key, history, login, logout, price_estimator, and register.

#### Index:
This route handles the main feature of this web application: Tailoring the user's resume to a job description. 

When accessed using "POST", this route will ensure the user entered a target job title, target industry, target company, job description, and resume. In additional to ensuring the user has entered all required fields, it will verify that the target job title, target company, and target industry are within certain character limits. The job description and resume have character maximums and minimums to try and prevent bad actors. If any of these limits are exceeded or if the user does not yet have an OpenAI API key saved, the function will return an error to the user describing what is wrong.

If all checks are passed, the function will use the users OpenAI API key and a the 'get_imp_resp' function from helpers to get the 3 most important responsibilities from the job description. These responsibilities are then formatted into HTML using markdown. This process is repeated to get the tailored resume and differences between the tailored resume and new resume, but using the 'get_tailored_resume' and 'get_differences' functions from helpers.

A resume name is then generated using the target company and target job title. This name, along with the target job title, target industry, target company, tailored resume, and date and time that the resume was generated, are stored in the history database for the user. If there are already 5 documents stored for that particular user, the oldest document is overwritten with the resume that has just been generated.

Finally, the HTML versions for the 3 most important responsibilities, tailored resume, and differences between the two resumes are sent to the JavaScript in the front end to dynamically insert into the web page.

When accessing this route using "GET" the page will load with the required input boxes. If the user has previously entered a resume in the account page, that user's resume will be selected and entered into the resume field.

#### About:
This route simply renders the about.html template that describes what this web application does.

#### Account:
This route allows the user to update: email, password, OpenAI API Key, and resume.

When accessed using "POST", this route will ensure the user entered an email and OpenAI API Key. If the user has previously entered these values, they will autofill into the input boxes. The function then verifies that the passwords match if they were changed and the password is different from the one saved. Next, it ensures the email and/or OpenAI API Key are the same as what is in the database and if not, the email and/or API Key are updated. Finally the resume length is checked if it was entered and if it is within the length requirements, it is saved into he database.

A message is then sen to the JavaScript using 'jsonify' to update the user with the errors or successful fields updated in the database.

When accessing this route using "GET" the page will load with the required input boxes. If the user has previously entered an email, OpenAI Key, or resume, those fields will autofill in.

### helper.py:
### resi.db

## Design Decisions:
### Models:
This web application uses OpenAI's gpt-3.5-turbo-1106 and gpt-4-1106-preview models. The GPT-3.5 Turbo model is used to generate the 3 most important responsibilities from the job description. This model showed consistent and accurate results for generating the 3 most important responsibilities similar to GPT-4 Turbo, but it was able to do so quicker and cheaper than GPT-4, so it was chosen for the initial task of finding the three most important responsibilities in the job description.

The GPT-4-Turbo model was chosen to generate the tailored resume due to its superior performance when it came to accuracy and consistency. GPT-3.5-Turbo was faster and cheaper, but it came at the cost of providing inaccurate tailored resumes and especially when it came to comparing between the tailored and original resumes. The decreased speed and increased cost were deemed worthwhile for the improved accuracy and consistency. GPT-4-Turbo appears to do much better then GPT-3.5-Turbo with the additional content that was required for this application.

Original versions of this application used gpt-3.5-turbo which resulted in inaccurate results and it lacked the context window required to handle the resumes and job descriptions. The gpt-4 model was also tested, however it was too slow and also lacked the context window required to be considered functional for this application.

### Prompts:
The prompts used to 
#### Security:

