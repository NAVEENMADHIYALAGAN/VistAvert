from geopy.geocoders import Nominatim
import folium
from geopy.distance import geodesic

def get_coordinates(location):
    geolocator = Nominatim(user_agent="my_geocoder", timeout=10)  
    location = geolocator.geocode(location)
    return location.latitude, location.longitude

def calculate_midpoint(coord1, coord2):
    return (coord1[0] + coord2[0]) / 2, (coord1[1] + coord2[1]) / 2

def display_map(source, destination, midpoint, map_filename):
    m = folium.Map(location=midpoint, zoom_start=6)

    folium.Marker(source, popup='Source').add_to(m)
    folium.Marker(destination, popup='Destination').add_to(m)
    folium.Marker(midpoint, popup='Midpoint').add_to(m)

    folium.PolyLine(locations=[source, destination], color='blue').add_to(m)
    folium.PolyLine(locations=[source, midpoint], color='green').add_to(m)
    folium.PolyLine(locations=[midpoint, destination], color='red').add_to(m)

    m.save(map_filename)

if __name__ == "__main__":
    source_location = input("Enter source location: ")
    destination_location = input("Enter destination location: ")

    source_coords = get_coordinates(source_location)
    destination_coords = get_coordinates(destination_location)

    midpoint_coords = calculate_midpoint(source_coords, destination_coords)

    distance = geodesic(source_coords, destination_coords).kilometers

    print("Midpoint Coordinates:", midpoint_coords)
    print("Distance between source and destination:", distance, "km")

    map_filename = "map.html"
    display_map(source_coords, destination_coords, midpoint_coords, map_filename)
    print(f"Map saved as {map_filename}")
