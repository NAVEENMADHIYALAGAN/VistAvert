import pandas as pd
from sklearn.cluster import KMeans
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

def main():
    # Load your dataset
    try:
        dataset = pd.read_csv(r'C:\Users\navee\OneDrive\Desktop\Project\New folder\updated_dataset.csv')
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return

    # Print dataset information

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

def get_cluster(location, dataset):
    # Find the row in the dataset corresponding to the location
    row = dataset[dataset['district'] == location]

    # If the location is not found in the dataset, return None
    if row.empty:
        print(f"Location '{location}' not found.")
        return None

    # Otherwise, return the cluster label for the location
    return row['Cluster'].iloc[0]

if __name__ == "__main__":
    main()
