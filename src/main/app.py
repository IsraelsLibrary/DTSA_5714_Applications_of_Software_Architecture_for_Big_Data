# Importing required libraries
import requests
from flask import Flask, request, jsonify

import pandas as pd
import numpy as np
import sqlite3
import time
import json

from sklearn.linear_model import LogisticRegression

# Setting up the Flask app
app = Flask(__name__)
app.start_time = time.time()
app_metrics = {"Number of Requests":0, "Total Response Time":0.0, "Requests Per Second":0.0}
app_health = {"Health Status": ""}
db_results = []


# Method that returns a list of exhibitions (ongoing and current) based on a given artist and US state
def get_exhibition_news(artist_name, state):
    # Define the Google Places API key to retrieve the required data.
    api_key = "GOOGLE PLACES API KEY"

    # Define the URL address for the Google Places API
    url_address = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    exhibitions = []

    # Define the search query
    query = f"{artist_name} exhibitions in {state}"

    # Set up parameters for the API request
    params = {
        "query": query,
        "key": api_key
    }

    # Send the API request
    response = requests.get(url_address, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])

        # Extract and print exhibition details
        for i, result in enumerate(results, start=1):
            exhibitions.append({"Exhibition":i, "Name": result['name'],
                                "Address": result['formatted_address'],
                                "Rating": result.get('rating', 'N/A')})
        return exhibitions
    else:
        return f"Failed to retrieve exhibitions list for {artist_name} in {state}. Status code: {response.status_code}"

# Method that utilizes machine learning by applying a Logistic Regression model to a given dataset. The model
# optimizes the search of exhibitions based on the rating for each exhibition, and then sorts the
# exhibitions list based on predicted results.
def apply_ml_model(data):
    # Convert the input data into a dataframe
    df = pd.DataFrame(data)

    # Produce a column of numeric representations to correspond to the address of each exhibition.
    df['Address_num'] = pd.to_numeric(df['Address'], errors='coerce')
    df['Address_num'] = df['Address_num'].apply(lambda x: np.random.choice([0, 1]) if pd.isna(x) else x)

    # Split the data and prepare it for training the model.
    X = df[["Exhibition", "Rating"]]
    y = df["Address_num"]

    model = LogisticRegression()

    try:
        model.fit(X,y)
    except Exception as e:
        return f"Unable to return results at this time. Please try again."
    except ValueError as ve:
        return f"Unable to return results at this time. Please try again."


    predictions = model.predict(X)

    # Copy the original dataframe and insert the predicted results as a new column. Return the new dataframe,
    # sorted by predicted values.
    modified_df = df.copy()
    modified_df['predictions'] = predictions
    modified_df = modified_df.sort_values(by='predictions')
    return modified_df


# Method that returns a list of art museums based on a given state.
def find_state_art_museums(state):
    # Define the Google Places API key to retrieve the required data.
    api_key = "GOOGLE PLACES API KEY"

    # Set up the API endpoint URL address for the initial search
    search_endpoint = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    # Define the search query to find art museums in the given state
    query = f"art museums in {state}"

    # Set up the parameters for the search request
    search_params = {
        "query": query,
        "key": api_key,
    }

    # Send a GET request to the search API
    search_response = requests.get(search_endpoint, params=search_params)

    # Check if the search request was successful
    if search_response.status_code == 200:
        search_data = search_response.json()
        results = search_data.get("results", [])

        # Create a list of museums with their names and place IDs
        museums = []
        for result in results:
            museum_name = result["name"]
            place_id = result["place_id"]
            museums.append({"name": museum_name, "place_id": place_id})

        # Set up the API endpoint URL for details requests
        details_endpoint = "https://maps.googleapis.com/maps/api/place/details/json"

        # Create a list of dictionaries containing museum names and websites
        art_museums_with_websites = []
        for museum in museums:
            # Set up the detail parameters for the search request
            details_params = {
                "place_id": museum["place_id"],
                "key": api_key,
            }

            # Send a GET request to the details API endpoint for the given search parameters
            details_response = requests.get(details_endpoint, params=details_params)

            # Confirm if the details request was successful
            if details_response.status_code == 200:
                details_data = details_response.json()
                result = details_data.get("result", {})

                # Get the website for a given museum or return the error statement is website is not found
                website = result.get("website", "Website not available")

                art_museums_with_websites.append({"name": museum["name"], "website": website})
            else:
                print(f"Error: {details_response.status_code} - {details_response.text}")

        return art_museums_with_websites
    else:
        print(f"Error: {search_response.status_code} - {search_response.text}")
        return f"Error: {search_response.status_code} - {search_response.text}"


# Method that returns a database name, based on a given artist name and state
def database_name(artist_name, state):
    database_name = f"finalproject_database_{artist_name}_{state}.db"
    return database_name.replace(" ", "")

# Method that saves data to a local SQLite database, based on input data and a given table name
def save_to_database(data, artist_name, state, table_name):
    database_name = f"finalproject_database_{artist_name}_{state}.db"

    try:
        # Connect to the SQLite database (or create it if it doesn't exist)
        connection = sqlite3.connect(database_name.replace(" ", ""))
        cursor = connection.cursor()

        # Create a table (if it doesn't exist) to store the serialized dictionary
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')

        # Serialize the dictionary and insert it into the database
        serialized_dict = str(data)
        cursor.execute(f'''
            INSERT INTO {table_name} (data)
            VALUES (?)
        ''', (serialized_dict,))

        # Commit the changes and close the connection
        connection.commit()
        connection.close()

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")


# Method that updates application metrics based on the response time
def update_app_metrics(response_time):
    app_metrics["Number of Requests"] += 1
    app_metrics["Total Response Time"] += response_time
    total_time = time.time() - app.start_time
    app_metrics["Requests Per Second"] = app_metrics["Number of Requests"] / total_time


# Method that checks the health of the application based on whether a database was successfully
# created at the end of the application process.
def check_app_health(database):
    try:
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT 1')
            verification = cursor.fetchone()
            if verification[0]==1:
                return "Health Status: Application is healthy", 200
    except Exception as e:
        return f"Health Status : Application is Not Healthy, Error: {str(e)}", 500

# Method and endpoint for setting up contents for the html file
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Artwork Locations Search</title>
    </head>
    <body>
        <h1>Search for State Museum and Exhibition Locations For A Given Artist</h1>
        <form method="POST" action="/search">
            <label for="artist_name">Artist Name:</label>
            <input type="text" name="artist_name" required><br><br>
            <label for="state">Local State:</label>
            <input type="text" name="state" required><br><br>
            <input type="submit" value="Search">
        </form>
    </body>
    </html>
    """

# Creating the health endpoint
@app.route('/health')
def app_health_func():
    return app_health


# Creating the metrics endpoint
@app.route('/metrics')
def capture_metrics():
    metrics = {"Number of Requests": app_metrics["Number of Requests"],
               "Total Response Time": app_metrics["Total Response Time"],
               "Requests Per Second": app_metrics["Requests Per Second"],
               }

    return metrics


# Creating the database endpoint that returns the database results
@app.route('/database_results')
def database_results():
    return db_results



# Method that executes the entire process and includes the following operations: creates a list of state museums and
# their websites, creates a list of state exhibitions for a given artist, stores both results in their own respective
# databases, and posts the results to the HTML page.
@app.route('/search', methods=['POST'])
def search():
    artist_name = request.form['artist_name']
    state = request.form['state']

    # Generate the list of art museums and websites for a given state. Save the results to a local database.
    request_start_time = time.time()
    artwork_locations = find_state_art_museums(state)
    update_app_metrics(time.time() - request_start_time)
    result_html = f"<h1>Museum Locations in {state}</h1>"

    # Generate the list of exhibitions for a given artist and state. Apply machine learning to optimize the
    # list of exhibition results. Store the results into a separate database.
    if artwork_locations:
        result_html += "<ul>"
        for location_name in artwork_locations:
            save_to_database({'Museum Name':location_name['name'], 'Museum Website':location_name['website']},
                             artist_name, state, "Museum_Locations")
            db_results.append({'Museum Name':location_name['name'], 'Museum Website':location_name['website']})
            museumdb_name = database_name(artist_name, state)
            app_health["Health Status"] = check_app_health(museumdb_name)
            exhibitions = get_exhibition_news(artist_name, state)
            ml_results = apply_ml_model(exhibitions)
            result_html += f"<li>Museum Name: {location_name['name']}, website: {location_name['website']}</li>"
        result_html += f"<h1>{artist_name} Exhibitions in {state}</h1>"
        for ind, name in enumerate(ml_results['Name']):
            result_html += f"<li>Name: {name}, Address: {ml_results['Address'][ind]}</li>"
            save_to_database({"Name": name, "Address": ml_results['Address'][ind]}, artist_name,
                             state, "Exhibitions")
            db_results.append({"Name": name, "Address": ml_results['Address'][ind]})
            exhibitionsdb_name = database_name(artist_name, state)
            app_health["Health Status"] = check_app_health(exhibitionsdb_name)
        result_html += "</ul>"
    else:
        result_html += "<p>No artwork locations found for the specified artist in the given state.</p>"
    result_html += '<a href="/">Back to Search</a>'

    # Return the HTML results
    return result_html


if __name__ == '__main__':
    app.run(debug=True)
