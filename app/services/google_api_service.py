import requests

def getGoogleRoutes(GOOGLE_API_KEY,source, destination):
    """    Function to get Google Maps directions between two locations.
    Args:
        GOOGLE_API_KEY (str): Your Google Maps API key.
        source (str): The starting location.
        destination (str): The destination location."""
    if not GOOGLE_API_KEY:
        raise ValueError("Google API key is not provided.")
    url= f"https://maps.googleapis.com/maps/api/directions/json?sensor=false&\
                mode=driving&alternatives=true&destination={destination}&origin={source}&key={GOOGLE_API_KEY}"

    payload = {}
    headers = {}
    try:
        data = requests.request("GET", url, headers=headers, data=payload).json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

    routes=[]

    best_lat_long=[]
    for lat_long in data["routes"][0]["legs"][0]["steps"]:
        best_lat_long.append(lat_long['end_location'])
    best_lat_long = [{'latitude': item['lat'], 'longitude': item['lng']} for item in best_lat_long]      
        
    routes.append({"best" : {"summary":data["routes"][0]["summary"],
                        "distance":data["routes"][0]["legs"][0]["distance"]["text"],
                        "duration":data["routes"][0]["legs"][0]["duration"]["text"],
                        "overview_polyline_points":data["routes"][0]["overview_polyline"]["points"],
                        "lat_long": best_lat_long
                        }})
    

    alternate_lat_long=[]
    for lat_long in data["routes"][1]["legs"][0]["steps"]:
        alternate_lat_long.append(lat_long['end_location'])
    alternate_lat_long = [{'latitude': item['lat'], 'longitude': item['lng']} for item in alternate_lat_long]      

    routes.append({"alternate" : {"summary":data["routes"][1]["summary"], 
                        "distance":data["routes"][1]["legs"][0]["distance"]["text"],
                        "duration":data["routes"][1]["legs"][0]["duration"]["text"],
                        "overview_polyline_points":data["routes"][1]["overview_polyline"]["points"],
                        "lat_long": alternate_lat_long
                        }})    


    return routes[0]['best'], routes[1]['alternate']
