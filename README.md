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

## File Breakdown:
### app.py:
Anytime a resume or job description is entered, the Flask backend will verify that the number of characters used is roughly within the expected limits for a resume or job description. If not, it will return an error to the user specifying what went wrong.
### helper.py:
#### Prompts:
#### Security:

### resi.db