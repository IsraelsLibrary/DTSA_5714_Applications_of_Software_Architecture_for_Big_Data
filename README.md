# DTSA 5714 Applications of Software Architecture For Big Data - Final Project

## Description
An 'art exhibition' finder application that returns two set of results: 
1.) A list of state-level art museums and their corresponding websites, 
2.) A list of state-level exhibitions for a given artist

Users must provide an artist name and state name in order to begin the application process.

## Instructions for running the application

Run the included YAML file to update the CI/CD pipeline for the application.

To run the program, make sure to have Python installed and all required Python libraries. Run the 'app.py' in the 'src' directory with the following terminal command:

'python app.py'

Once the application starts, the following application endpoints can be accessed manually by running their addresses in a web browser. **Bear in mind the results WILL NOT show on additional endpoints until the user provides input to the main application and produces a list of exhibition results.**

Main application:
http://127.0.0.1:5000

Application health endpoint:
http://127.0.0.1:5000/health

Application metrics endpoint:
http://127.0.0.1:5000/metrics

Application Database Results endpoint:
http://127.0.0.1:5000/database_results




## Authors and acknowledgment
Israel Johnson

## License
For open source projects, say how it is licensed.
