import requests
import polyline

def extract_polyline(steps):
    polylines = []
    for step in steps:
        if 'polyline' in step:
            polylines.append(step['polyline']['points'])
    return polylines


def extract_lat_lng(steps):
    lat_lng_list = []
    for step in steps:
        if 'polyline' in step:
            points = polyline.decode(step['polyline']['points'])
            lat_lng_list.extend([(point[1], point[0]) for point in points])
    return lat_lng_list


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

    best_route_points=extract_lat_lng(data['routes'][0]['legs'][0]['steps'])
    best_polyline_points=extract_polyline(data['routes'][0]['legs'][0]['steps'])

    routes.append({"best" : {"summary":data["routes"][0]["summary"],
                        "distance":data["routes"][0]["legs"][0]["distance"]["text"],
                        "duration":data["routes"][0]["legs"][0]["duration"]["text"],
                        "overview_polyline_points":data["routes"][0]["overview_polyline"]["points"],
                        "lat_long": best_lat_long,
                        "route_points": best_route_points,
                        "polyline_points": best_polyline_points
                        }})
    # Check if there is an alternate route
    if len(data["routes"]) >1:
        alternate_lat_long=[]
        for lat_long in data["routes"][1]["legs"][0]["steps"]:
            alternate_lat_long.append(lat_long['end_location'])
        alternate_lat_long = [{'latitude': item['lat'], 'longitude': item['lng']} for item in alternate_lat_long]
        best_polyline_points=extract_polyline(data['routes'][1]['legs'][0]['steps'])
        alternate_route_points=extract_lat_lng(data['routes'][1]['legs'][0]['steps'])
        routes.append({"alternate" : {"summary":data["routes"][1]["summary"], 
                        "distance":data["routes"][1]["legs"][0]["distance"]["text"],
                        "duration":data["routes"][1]["legs"][0]["duration"]["text"],
                        "overview_polyline_points":data["routes"][1]["overview_polyline"]["points"],
                        "lat_long": alternate_lat_long,
                        "route_points": alternate_route_points,
                        "polyline_points": best_polyline_points
                        }})   
    else:
        routes.append({"alternate" : {"summary":"No alternate route found", 
                        "distance":"",
                        "duration":"",
                        "overview_polyline_points":"",
                        "lat_long": "",
                        "route_points": ""
                        }}) 

    return routes[0]['best'], routes[1]['alternate']
