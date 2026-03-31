
This is the AI usage docuemnt.

## Tool used
I used ChatGPT for this assignment, as development assistant for the Job Application Tracker course project. 
This AI tool was used to help me with code structure, debugging, Flask route design, MySQL connection troubleshooting, HTML template generation, and understanding project requirements.

## Key Prompts Used
1. "Help me design the MySQL schema for the Job Application Tracker project using the required four tables."
2. "Create a database.py file with a reusable MySQL connection helper and CRUD functions for companies, jobs, applications, and contacts."
3. "Help me troubleshoot MySQL connection errors in Python using Flask and mysql-connector-python."
4. "Generate Flask CRUD routes for app.py for companies, jobs, applications, and contacts."
5. "Create HTML templates for a Flask job application tracker project with dashboard, form pages, list pages, and job match page."
6. "Help me create a job match feature that compares entered skills to job requirements stored in a JSON field."
7. "Help me fix Git issues when committing and pushing files to GitHub."

## What AI Helped Generate
- Initial database connection structure for `database.py`
- CRUD function layout for all four tables
- Flask route structure in `app.py`
- HTML templates inside the `templates` folder
- Guidance for `.env` configuration and `.gitignore`
- Help with job match percentage logic
- Debugging help for MySQL login issues and Git errors

## Changes I Made to the AI Output
- Updated database credentials to work with my local MySQL environment
- Changed the `.env` settings and database user after troubleshooting MySQL authentication
- Tested and corrected the generated code in my local environment
- Adjusted project files and GitHub structure to match the course project requirements
- Verified that routes, templates, and database functions worked together correctly
- Added my own data and project video for the final repository

## What Worked Well
- The overall Flask application structure worked well and allowed me to organize the project into clear components such as routes, database logic, and templates.
- Separating database logic into a dedicated `database.py` file made the code easier to manage and debug.
- Implementing CRUD operations step by step for each table helped ensure that each part of the application functioned correctly before moving on.
- The HTML templates provided a clean and consistent user interface across all pages.
- Using environment variables for database configuration improved flexibility and made it easier to manage connection settings.
- The job match feature worked effectively by comparing user-entered skills with job requirements stored in the database.
- Frequent testing during development helped identify and fix issues early, especially with database connections and routing.

## What Did Not Work Perfectly at First
- Some generated steps needed adjustment based on my local setup
- MySQL authentication required additional troubleshooting
- I had to test and fix environment variable usage before the connection worked
- Some Git steps required correction when local and remote repositories were out of sync

## Lessons Learned
- AI can speed up development, but the code still needs to be tested carefully
- Environment variables are important for keeping database credentials separate from code
- CRUD applications work better when database logic is separated into a dedicated file like `database.py`
- Flask routing and HTML templates must match exactly for the app to run correctly
- Debugging step by step is important when dealing with MySQL, Git, and local environment issues
- AI is most useful when I ask clear, specific questions and then verify the results myself

## Overall Reflection
Using AI helped me complete the project faster and understand how the pieces of a full-stack web application fit together. It was especially useful for troubleshooting, code generation, and organization. I also learned that AI-generated code should always be tested, reviewed, and adapted to the actual project requirements and local environment.
