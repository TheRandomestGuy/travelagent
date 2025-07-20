import requests
import os
from dotenv import load_dotenv

load_dotenv()

def poi_list(location_name, radius):
    geocode_url = f"https://api.opentripmap.com/0.1/en/places/geoname"
    geocode_params = {
        'name': location_name,
        'lang': 'en',
        'apikey': os.getenv('OPEN_TRIP_MAP_API_KEY')
    }
    geocode_response = requests.get(geocode_url, params=geocode_params)
    geocode_data = geocode_response.json()
    if 'lat' not in geocode_data or 'lon' not in geocode_data:
        print("Error: Unable to find city coordinates.")
        return []
    lat, lon = geocode_data['lat'], geocode_data['lon']

    poi_url = f"https://api.opentripmap.com/0.1/en/places/radius"
    poi_params = {
        'radius': radius,
        'lon': lon,
        'lat': lat,
        'kinds': 'interesting_places,adult,amusements,sport,tourist_facilities',
        'apikey': os.getenv('OPEN_TRIP_MAP_API_KEY')
    }
    poi_response = requests.get(poi_url, params=poi_params)
    poi_data = poi_response.json()
    if 'features' not in poi_data:
        print("Error: Unable to fetch POIs.")
        return []
    pois = []
    for feature in poi_data['features']:
        name = feature['properties'].get('name', 'Unknown')
        point = feature['geometry']['coordinates']
        pois.append({'name': name, 'coordinates': point})
    return pois

def travel_time(location_cords1, location_cords2):
    dist_matrix_url = f"https://api.openrouteservice.org/v2/matrix/driving-car"

    body = {"locations":[location_cords1,location_cords2]}
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': os.getenv('OPEN_ROUTE_API_KEY'),
        'Content-Type': 'application/json; charset=utf-8'
    }

    call = requests.post(dist_matrix_url, json=body, headers=headers).json()

    return call['durations'][0][1]

# if __name__ == "__main__":
#     city = "paris"
#     radius = 2000  # 2 km
#     pois = poi_list(city, radius)
#     print(pois)
#     for poi in pois:
#         print(f"Name: {poi['name']}, Coordinates: {poi['coordinates']}")

#     location1 = (2.3376, 48.8606)  # Lourve
#     location2 = (2.2945,48.8584)  # Eiffel Tower
#     travel_time = travel_time(location1, location2)
#     print(f"Travel time from {location1} to {location2}: {travel_time} seconds")

