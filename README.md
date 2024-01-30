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

If all checks are passed, the function will use the users OpenAI API key and a the `get_imp_resp` function from helpers to get the 3 most important responsibilities from the job description. These responsibilities are then formatted into HTML using markdown. This process is repeated to get the tailored resume and differences between the tailored resume and new resume, but using the `get_tailored_resume` and `get_differences` functions from helpers.

A resume name is then generated using the target company and target job title. This name, along with the target job title, target industry, target company, tailored resume, and date and time that the resume was generated, are stored in the history database for the user. If there are already 5 documents stored for that particular user, the oldest document is overwritten with the resume that has just been generated.

Finally, the HTML versions for the 3 most important responsibilities, tailored resume, and differences between the two resumes are sent to the JavaScript in the front end to dynamically insert into the web page.

When accessing this route using "GET" the page will load with the required input boxes. If the user has previously entered a resume in the account page, that user's resume will be selected and entered into the resume field.

#### About:
This route simply renders the about.html template that describes what this web application does.

#### Account:
This route allows the user to update: email, password, OpenAI API Key, and resume.

When accessed using "POST", this route will ensure the user entered an email and OpenAI API Key. If the user has previously entered these values, they will autofill into the input boxes. The function then verifies that the passwords match if they were changed and the password is different from the one saved. Next, it ensures the email and/or OpenAI API Key are the same as what is in the database and if not, the email and/or API Key are updated. Finally the resume length is checked if it was entered and if it is within the length requirements, it is saved into he database.

A message is then sent to the JavaScript using `jsonify` to update the user with the errors or successful fields updated in the database.

When accessing this route using "GET" the page will load with the required input boxes. If the user has previously entered an email, OpenAI Key, or resume, those fields will autofill in.

#### API Key:
This route allows the user to update their OpenAI API Key.

When accessed using "POST", this route will ensure that the user entered an API Key. It will pull the user's Open API Key from the SQL database. If no API Key is found in the database, it will validate the user's entered API Key and save it into the database. If there is an API Key already in the database, it will verify that the entered API Key is different before validating and updating the database.

A message is then sent to the JavaScript using `jsonify` to update the user with the errors or successful fields updated in the database.

When accessing this route using "GET" the page will render a template with instructions for how to get an OpenAI API Key and an input box for the API Key. If the user has previously entered an OpenAI API Key the input field will autofill in.

#### History:
This route will obtain all the documents the user has saved in the the database and render them in a template. The documents are displayed in descending order by date.

#### Login:
This route will login the user given the correct login information is given.

When accessed using "POST", the route will check if the user has entered an email and password, then check the database to determine if the email is saved. If a matching email is found in the database, it will check that the password matches the one in the database for the given email and set the session to the user's id number before redirecting them to the index page.

If any errors are found, the user will be redirected to an apology page explaining what went wrong.

When accessing this route using "GET" the page will render a template with the login input boxes.

#### Logout:
This route will logout the user by clearing their session and redirecting them to the login page.

#### Price Estimator:
This route will take the job description and user's resume and determine a rough estimate of how much it would cost to generate a tailored resume.

When accessed using "POST", the route will check that the user has entered a job description and resume that fall within certain length requirements. Next, it will lookup the user's OpenAI API Key in the database and use the `price_estimator_prompts` function to get example input and output prompts for estimation. These prompts are then fed into the `price_estimation` with the OpenAI API Key and a new page is rendered with the estimate price.

When accessing this route using "GET" the page will render a template with input boxes for the job description and resume.  The resume input will autofill if a resume is saved in the system.

#### Register:
This route allows the user to register using an email and password.

When accessed using "POST", the route will check that the user entered an email, password, and confirmation of password. Next, it checks that the password and confirmation match and that the email is not already contained in the database. Finally, it sets the new session for the user and enters the email and hashed password into the database before redirecting the logged in user to the api_key route.

If any errors are found, the user will be redirected to an apology page explaining what went wrong.

When accessing this route using "GET" the page will render a template with the register input boxes.


### helper.py:
This is the helper file where all helpful functions for app.py are stored. This file contains the following functions:

#### api_key_validation
This function is used to determine if the user has entered a valid OpenAI API Key.

This function takes the `user_api_key` and returns true if the key is valid and false if not. The function will try a test call to OpenAI's gpt-3.5-turbo-1106 model and if a response is returned, the function will return true, else it will return false.

#### apology
This function is used to deliver a custom apology message to a user.

This function will take a `message` and error `code` and return a rendered template with the code and message to be used to display to the user what has gone wrong. This function will also convert any unknown symbols to known symbols. For the meme generator in apology.html.

#### decrypt_key
This function is used to decrypt the user's encrypted OpenAI API Key when it is retrieved from the database.

The function will take an `encrypted_key` and `fernet_instance` and return a decrypted OpenAI API Key that can be used to access OpenAI's API.

#### encrypt_key
This function is used to encrypt the user's OpenAI API Key when it is retrieved from the user to be updated in the database.

The function will take a `key` and `fernet_instance` and return a encrypted OpenAI API Key to be store in the database.

#### get_fernet_instance
This function will initialize and return a Fernet instance using a secret key from the server side.

The function will open a text file stored outside of the project file directory that stores the secret key for access to the OpenAI API Keys that are stored in the database. Any one wishing to clone this repository will need to generate their own secret key and save it to a file on their local machine. This allows for public sharing of this repository without jeopardizing any user's OpenAI API Key.

#### get_imp_resp
This function will use OpenAI's API to generate the 3 most important job responsibilities from the user's input of industry and job description.

The function will take the an OpenAI `api_key`, `industry`, `jobdescription`, and `temp` that is automatically set to 0.5 for a balanced response. Using this information, the function will enter the required information into the prompts that will be sent to OpenAI's model and will return the model's response in markdown. This function uses the gpt-3.5-turbo-1106 model for speed and low cost with out lose to accuracy.

#### get_differences
This function will use OpenAI's API to generate a table of the differences between the user's resume and the tailored resume from the user's input and previous OpenAI generations.

The function will take the an OpenAI `api_key`, `original_resume`, `tailored_resume`, and `temp` that is automatically set to 1 for a more creative response. Using this information, the function will enter the required information into the prompts that will be sent to OpenAI's model and will return the model's response in markdown for the differences between the original and tailored resume. This function uses the gpt-4-1106-preview model for increased accuracy and reliability in responses. The top_p is set to 0.9 to cut down some of the responses that the model considers to improve speed marginally.

#### get_tailored_resume
This function will use OpenAI's API to generate a tailored resume based on the user's input information and previous OpenAI generations.

The function will take the an OpenAI `api_key`, `company`, `imp_resp`, `industry`, `jobdescription`, `jobtitle`, `resume`, and `temp` that is automatically set to 1 for a more creative response. Using this information, the function will enter the required information into the prompts that will be sent to OpenAI's model and will return the model's response in markdown for a resume tailored to a specific job description. The entered information is used to improve the prompt for the model to improve the response for the user. This function uses the gpt-4-1106-preview model for increased accuracy and reliability in responses. The top_p is set to 0.8 to cut down some of the responses that the model considers to improve speed marginally.

#### login_required
This function will decorate any routes that require login. If the user is not logged in, they will be redirected to the login route.

#### price_estimator_prompts
This function takes a job description and resume and creates example input and output prompts that it would expect from tailoring a resume.

The function will take a `jobdescription` and `resume` and generate two dictionaries: price_estimate_inputs and price_estimate_outputs. These dictionaries will contain the inputs and estimated outputs of the model to determine how many tokens the user is likely going to use.

#### price_estimation
This function takes an OpenAI API Key and a dictionary of potential inputs and outputs for tailoring a resume and returns the expected price of that API call.

The function will take an OpenAI `user_api_key`, `price_estimate_inputs` and `price_estimate_outputs` and makes an API call to OpenAI with a max token response limit of 1 token. From this response, the function pulls the token count for the inputs and outputs using the gpt-4-1106-preview model and multiples the toke count for each by the price per 1k tokens for the gpt-4-1106-preview model and returns the sum.

#### usd
This function will format a value into United State's dollars.

### resi.db:
This is the main SQL database that stores the user's email, password, OpenAI API Key, resume, and any generated documents. The database contains two tables: users and history. All information that is entered into the database is sanitized using the `?` operator to prevent against injection attacks.

#### users:
The users table stores the following information:
- id: auto incrementing integer to keep track of the user (Primary Key)
- email: unique index to store the user's identifying email as text
- hash: text input to store the hash of the user's password
- api_key: text input to store the user's encrypted OpenAI API Key
- resume: text input to store the user's original resume

#### history:
The history table stores the following information:
- id: auto incrementing integer to keep track of the document created (Primary Key)
- user_id: integer to keep track of which user created a particular document (Foreign Key references users(id))
- document_name: text input to store the name of the document created
- company: text input to store the name of the target company the document was created for
- job_title: text input to store the target job title the document was created for
- document: text input to store the document that the user created
- datetime: text input to store when the document was created

Note: Only the 5 most recent documents are stored to prevent the database from being overcrowded with too many documents.


## Design Decisions:
### Models:
This web application uses OpenAI's gpt-3.5-turbo-1106 and gpt-4-1106-preview models. The GPT-3.5 Turbo model is used to generate the 3 most important responsibilities from the job description. This model showed consistent and accurate results for generating the 3 most important responsibilities similar to GPT-4 Turbo, but it was able to do so quicker and cheaper than GPT-4, so it was chosen for the initial task of finding the three most important responsibilities in the job description.

The GPT-4-Turbo model was chosen to generate the tailored resume due to its superior performance when it came to accuracy and consistency. GPT-3.5-Turbo was faster and cheaper, but it came at the cost of providing inaccurate tailored resumes and especially when it came to comparing between the tailored and original resumes. The decreased speed and increased cost were deemed worthwhile for the improved accuracy and consistency. GPT-4-Turbo appears to do much better then GPT-3.5-Turbo with the additional content that was required for this application.

Original versions of this application used gpt-3.5-turbo which resulted in inaccurate results and it lacked the context window required to handle the resumes and job descriptions. The gpt-4 model was also tested, however it was too slow and also lacked the context window required to be considered functional for this application.

A consideration was made to fine tune a model to improve the results, but this would have been costly and similar results could be achieved using prompt engineering. Additionally, the model would have lost some of the customization that can be achieved with prompting. 

There is room for additional improvements on the models with improved prompting or settings that could not be covered at this time.

### Prompts:
The prompts used to generate the resumes were derived from the following YouTube video by Jeff Su: [Land a Job using ChatGPT: The Definitive Guide!](https://www.youtube.com/watch?v=pmnY5V16GSE&t=317s). The prompts were adjusted to fit the adjustable needs of this project.

The prompts have been designed to replicate how a sample conversation would go with ChatGPT, while having room to be customized to the user's particular situation.

### Security:
Security was a major concern on this project. The goal was for the project to be secure while also openly accessible for open source.

This was accomplished using hashes for the user's passwords so any database leaks would not result in passwords being leaked and using a secret key encryption to encrypt user's API Keys so that they cannot be decrypted by anyone other than the person who has set up the project.

All inputs into the databases are also sanitized to protect against injection attacks.

