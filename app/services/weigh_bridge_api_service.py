from shapely.geometry import LineString
import requests
import csv
from geopy.distance import geodesic
import time
from dotenv import load_dotenv
import os


load_dotenv()

# Retrieve the GOOGLE_API_KEY from the environment
API_KEY = os.getenv("GOOGLE_API_KEY")

def fetch_weighbridges(lat, lon, radius):
    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
        f"location={lat},{lon}&radius={radius}&keyword=weighbridge&key={API_KEY}"
    )
    response = requests.get(url)
    return response.json().get("results", [])

def fetch_place_details(place_id):
    url = (
        f"https://maps.googleapis.com/maps/api/place/details/json?"
        f"place_id={place_id}&fields=name,formatted_phone_number&key={API_KEY}"
    )
    response = requests.get(url)
    return response.json().get("result", {})


def extract_details(place):
    name = place.get("name", "")
    location = place["geometry"]["location"]
    lat = location["lat"]
    lon = location["lng"]
    place_id = place.get("place_id", "")
    details = fetch_place_details(place_id)
    contact = details.get("formatted_phone_number", "")
    return {
        "name": name,
        "contact": contact,
        "lat": lat,
        "lon": lon,
        "capacity": "N/A",
        "length": "N/A"
    }, place_id


def getWeighBridgeNearMe(header_validation,cursor, TABLE_WEIGH_BRIDGE,data):
    # This function retrieves the nearest weigh bridge to a given location.
    # It takes three parameters: header_validation for validating the request headers,
    # cursor for executing database queries, and TABLE_WEIGH_BRIDGE as the name of the table containing weigh bridge data.
    if not header_validation:
        return {"message": "Token is not valid"}, 401
    try:
        latitude = data['latitude']
        longitude = data['longitude']
    except KeyError:
        return {"message": "Invalid input"}, 400

    try:
        # API_KEY = "AIzaSyBBgZATqp-TE3cTtK6F7J8Q7zXm7Z4ueV8"
        RADIUS_LIMITS = [2000, 4000, 6000, 8000, 10000]
        # LOCATION = (28.6139, 77.2090)  # Example: New Delhi
        LOCATION = (latitude, longitude)  # User's location
        grouped_weighbridges = {} 


        fetched_places = set()

        for radius in RADIUS_LIMITS:
            km_label = f"{radius // 1000}km"
            grouped_weighbridges[km_label] = []
            print(f"Searching within {km_label}...")

            places = fetch_weighbridges(LOCATION[0], LOCATION[1], radius)

            for place in places:
                place_id = place.get("place_id")
                if place_id and place_id not in fetched_places:
                    data, place_id = extract_details(place)
                    # save_to_csv(data, km_label)
                    grouped_weighbridges[km_label].append(data)
                    fetched_places.add(place_id)
                    print(f"Saved: {data['name']} in {km_label}")
                    time.sleep(1)  # Avoid rate limit

        # Optional: show grouped summary
        for group, entries in grouped_weighbridges.items():
            print(f"\n{group}: {len(entries)} weighbridges")

        return grouped_weighbridges, 200
    except Exception as e:
        print(str(e))
        return {"message": "Internal Server Error"}, 500


def getWeightBridgeCount(header_validation,cursor, TABLE_WEIGH_BRIDGE):
    # This function retrieves the count of weigh bridges from the database.
    # It takes three parameters: header_validation for validating the request headers,
    # cursor for executing database queries, and TABLE_WEIGH_BRIDGE as the name of the table containing weigh bridge data.
    if not header_validation:
        return {"message": "Token is not valid"}, 401
    else:
        query = f"SELECT COUNT(*) FROM {TABLE_WEIGH_BRIDGE}"
        cursor.execute(query)
        result = cursor.fetchone()
        return {"count":result[0]}, 200
    

def getWeighBridgeAlongRoute(header_validation,cursor, TABLE_WEIGH_BRIDGE,data):
    # This function retrieves the weigh bridges along a specified route.
    # It takes three parameters: header_validation for validating the request headers,
    # cursor for executing database queries, and TABLE_WEIGH_BRIDGE as the name of the table containing weigh bridge data.
    if not header_validation:
        return {"message": "Token is not valid"}, 401
    # try:
    #     vehicle_type=data['vehicle_type']
    try:
        threshold_toll_distance = data['distance_threshold']
    except KeyError:
        threshold_toll_distance = 1500

    try:    
        location_lines = LineString([(loc['longitude'], loc['latitude']) for loc in data['points']])
      
        # Query the data base for given vehicle type and location 
        cursor.execute(f'''SELECT name,mobile,latitude,longitude,capacity,length
                         FROM {TABLE_WEIGH_BRIDGE} WHERE ST_DWithin(location::geography, 
                         ST_SetSRID(ST_GeomFromText(%s),4326), {threshold_toll_distance})''', (location_lines.wkt,))
        
        # Fetch all rows from database
        nearby_wb = cursor.fetchall()

        nearby_wb_data=[]
        for data in nearby_wb:
            temp_dict = {"name":data[0],"mobile":data[1],"latitude":data[2],"longitude":data[3],"capacity":data[4],"length":data[5]} 
            nearby_wb_data.append(temp_dict)
        return nearby_wb_data,200
    except Exception as e:
        print(str(e))
        return {"message": "Internal Server Error"}, 500  