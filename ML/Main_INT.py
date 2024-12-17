import pandas as pd
from sklearn.cluster import KMeans
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium

def main():
    # Load your dataset
    try:
        dataset = pd.read_csv('updated_dataset.csv')
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return

    # Print dataset information
    print(dataset.info())

    # Select relevant columns for clustering
    try:
        X = dataset[['total_accidents']]
    except KeyError:
        print("Column 'total_accidents' not found in the dataset. Please check the column name.")
        return

    # Initialize and fit KMeans clustering model
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(X)

    # Add cluster labels to the dataset
    dataset['Cluster'] = kmeans.labels_

    # Input source and destination location names from the user
    source_location = input("Enter source location (district name): ")
    destination_location = input("Enter destination location (district name): ")

    # Get cluster for source and destination locations
    source_cluster = get_cluster(source_location, dataset)
    destination_cluster = get_cluster(destination_location, dataset)

    if source_cluster is None or destination_cluster is None:
        print("Error: Unable to determine cluster for source or destination location.")
        return

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

    risk_percentage = risk_percentages.get((source_cluster, destination_cluster), None)

    if risk_percentage is None:
        print("Error: Unable to determine risk percentage.")
        return

    print("Risk Percentage:", risk_percentage, "%")

    # Get coordinates for source and destination locations
    source_coords = get_coordinates(source_location)
    destination_coords = get_coordinates(destination_location)

    if source_coords is None or destination_coords is None:
        print("Error: Unable to retrieve coordinates for source or destination location.")
        return

    # Display map with source, destination, and route between them
    display_map(source_coords, destination_coords)

def get_coordinates(location):
    geolocator = Nominatim(user_agent="my_geocoder", timeout=10)
    location = geolocator.geocode(location)
    if location is None:
        print(f"Location '{location}' not found.")
        return None, None
    else:
        return location.latitude, location.longitude

def get_cluster(location, dataset):
    # Find the row in the dataset corresponding to the location
    row = dataset[dataset['district'] == location]

    # If the location is not found in the dataset, return None
    if row.empty:
        print(f"Location '{location}' not found.")
        return None

    # Otherwise, return the cluster label for the location
    return row['Cluster'].iloc[0]

def display_map(source, destination):
    # Create a map centered at the midpoint of source and destination
    midpoint = calculate_midpoint(source, destination)
    m = folium.Map(location=midpoint, zoom_start=6)

    # Add markers for source and destination
    folium.Marker(source, popup='Source').add_to(m)
    folium.Marker(destination, popup='Destination').add_to(m)

    # Add polyline for route between source and destination
    folium.PolyLine(locations=[source, destination], color='blue').add_to(m)

    # Save map to an HTML file
    map_filename = "map.html"
    m.save(map_filename)
    print(f"Map saved as {map_filename}")

def calculate_midpoint(coord1, coord2):
    return [(coord1[0] + coord2[0]) / 2, (coord1[1] + coord2[1]) / 2]

if __name__ == "__main__":
    main()