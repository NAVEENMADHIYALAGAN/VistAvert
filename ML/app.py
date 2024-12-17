from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.cluster import KMeans
import requests

app = Flask(__name__)

# Load dataset
dataset = pd.read_csv(r'C:\Users\navee\OneDrive\Desktop\Project\WEBSITE\updated_dataset.csv')

# Select relevant columns for clustering
X = dataset[['total_accidents']]

# Initialize and fit KMeans clustering model
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X)
dataset['Cluster'] = kmeans.labels_

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    source_location = request.form['source_location']
    destination_location = request.form['destination_location']

    # Check if source and destination locations are in the dataset
    if source_location not in dataset['district'].values or destination_location not in dataset['district'].values:
        return jsonify({'error': 'Source or destination location not found in dataset.'})

    source_cluster = get_cluster(source_location)
    destination_cluster = get_cluster(destination_location)

    if source_cluster is None or destination_cluster is None:
        return jsonify({'error': 'Unable to determine cluster for source or destination location.'})

    risk_percentage = calculate_risk(source_cluster, destination_cluster)

    if risk_percentage is None:
        return jsonify({'error': 'Unable to determine risk percentage.'})

    # Fetch weather for source and destination
    source_weather = fetch_weather(source_location)
    destination_weather = fetch_weather(destination_location)

    return jsonify({
        'risk_percentage': risk_percentage,
        'source_weather': source_weather,
        'destination_weather': destination_weather
    })

def get_cluster(location):
    row = dataset[dataset['district'] == location]
    if row.empty:
        return None
    return row['Cluster'].iloc[0]

def calculate_risk(source_cluster, destination_cluster):
    # Assign risk percentage based on the clusters of source and destination (modify as needed)
    risk_percentages = {
        (0, 0): 10,  # Low risk to low risk
        (0, 1): 30,  # Low risk to moderate risk
        (0, 2): 60,  # Low risk to high risk
        (1, 0): 20,  # Moderate risk to low risk
        (1, 1): 40,  # Moderate risk to moderate risk
        (1, 2): 70,  # Moderate risk to high risk
        (2, 0): 50,  # High risk to low risk
        (2, 1): 70,  # High risk to moderate risk
        (2, 2): 90   # High risk to high risk
    }
    return risk_percentages.get((source_cluster, destination_cluster), None)

def fetch_weather(location):
    try:
        apiKey = "YOUR_OPENWEATHERMAP_API_KEY"
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={apiKey}&units=metric")
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        return {
            'weather': weather,
            'temperature': temperature,
            'humidity': humidity
        }
    except Exception as e:
        print("Error fetching weather data:", e)
        return {
            'weather': 'N/A',
            'temperature': 'N/A',
            'humidity': 'N/A'
        }

if __name__ == "__main__":
    app.run(debug=True)
