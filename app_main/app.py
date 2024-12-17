from flask import Flask, render_template, request
import requests
import pandas as pd
from sklearn.cluster import KMeans

app = Flask(__name__)

# Function to get weather data from OpenWeatherMap API
def get_weather(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

# Function to get distance between two locations using Bing Maps API
def get_distance(api_key, source, destination):
    url = f"https://dev.virtualearth.net/REST/v1/Routes/Driving?o=json&wp.0={source}&wp.1={destination}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200 and 'resourceSets' in data and data['resourceSets']:
        route = data['resourceSets'][0]['resources'][0]
        distance = route['travelDistance']
        return distance
    else:
        return None

# Function to perform KMeans clustering and get risk percentage
def get_risk_percentage(source_location, destination_location):
    # Load dataset
    dataset = pd.read_csv(r'C:\Users\navee\OneDrive\Desktop\Project_Main\app_main\updated_dataset.csv')  # Replace with your dataset path

    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(dataset[['total_accidents']])
    dataset['Cluster'] = kmeans.labels_

    # Convert input location strings to lowercase
    source_location = source_location.lower()
    destination_location = destination_location.lower()

    # Get cluster labels for source and destination locations
    source_cluster = get_cluster(source_location, dataset)
    destination_cluster = get_cluster(destination_location, dataset)

    if source_cluster is None or destination_cluster is None:
        return None

    # Define risk percentages
    risk_percentages = {
        (0, 0): 10, (0, 1): 30, (0, 2): 60,
        (1, 0): 20, (1, 1): 40, (1, 2): 70,
        (2, 0): 50, (2, 1): 70, (2, 2): 90
    }

    # Get risk percentage based on source and destination clusters
    return risk_percentages.get((source_cluster, destination_cluster), None)

# Helper function to get cluster label for a location
def get_cluster(location, dataset):
    row = dataset[dataset['district'].str.lower() == location]
    if row.empty:
        return None
    return row['Cluster'].iloc[0]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-weather-and-route', methods=['POST'])
def get_weather_and_route():
    # Replace 'YOUR_OPENWEATHERMAP_API_KEY' with your actual OpenWeatherMap API key
    weather_api_key = '6c9b4a46744fb80f220bf1fa00da1414'
    # Replace 'YOUR_BING_MAPS_API_KEY' with your actual Bing Maps API key
    bing_maps_api_key = 'AtyxleTP1e_8iyirfawqhe2We5Q6tXzjJXoado9jjuZGqr23aEkhLZORGxS3Q42V'

    # Get user input from the form
    source_city = request.form['source']
    destination_city = request.form['destination']

    # Get weather data for the specified locations
    weather_data_source = get_weather(weather_api_key, source_city)
    weather_data_destination = get_weather(weather_api_key, destination_city)

    # Get distance between source and destination cities
    distance_km = get_distance(bing_maps_api_key, source_city, destination_city)

    # Calculate risk percentage
    risk_percentage = get_risk_percentage(source_city, destination_city)

    return render_template('map_and_weather.html',
                           source_city=source_city,
                           destination_city=destination_city,
                           weather_data_source=weather_data_source,
                           weather_data_destination=weather_data_destination,
                           distance_km=distance_km,
                           risk_percentage=risk_percentage,
                           bing_maps_api_key=bing_maps_api_key)

if __name__ == '__main__':
    app.run(debug=True)
