
from flask import jsonify
from collections import defaultdict
from shapely.geometry import LineString


def getCngAlongRouteByPoints(header_validation,cursor, TABLE_CNG_STATIONS,data):
    if not header_validation:
        return {"message": "Token is not valid"}, 401
    
    try:
        threshold_toll_distance = data['distance_threshold']
    except KeyError:
        threshold_toll_distance = 1500

    try:    
        location_lines = LineString([(loc['longitude'], loc['latitude']) for loc in data['points']])
      
        # Query the data base for given vehicle type and location 
        cursor.execute(f'''SELECT name,latitude,longitude,phone,address
                         FROM {TABLE_CNG_STATIONS} WHERE ST_DWithin(location::geography, 
                         ST_SetSRID(ST_GeomFromText(%s),4326), {threshold_toll_distance})''', (location_lines.wkt,))
        
        # Fetch all rows from database
        nearby_wb = cursor.fetchall()

        nearby_wb_data=[]
        for data in nearby_wb:
            temp_dict = {"name":data[0],"latitude":data[1],"longitude":data[2],"phone":data[3],"address":data[4]} 
            nearby_wb_data.append(temp_dict)
        return nearby_wb_data,200
    except Exception as e:
        print(str(e))
        return {"message": "Internal Server Error"}, 500  


def get_nearby_cng_stations(header_validation,cursor, TABLE_CNG_STATIONS,data):
    if not header_validation:
        return {"message": "Token is not valid"}, 401
    try:
        # Extract latitude and longitude from the input data
        current_latitude = float(data['latitude'])
        current_longitude = float(data['longitude'])
    except KeyError:
        return {"message": "Invalid input"}, 400
    

    try:
        # SQL query
        sql = f"""
                SELECT 
                    name,latitude,longitude,phone,address,
                    ST_DistanceSphere(ST_MakePoint(longitude, latitude),ST_MakePoint(%s, %s)) AS distance_meters,
                    CASE
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 10000 THEN 'within_10_kms'
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 20000 THEN 'within_20_kms'
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 30000 THEN 'within_30_kms'
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 40000 THEN 'within_40_kms'
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 50000 THEN 'within_50_kms'
                        ELSE NULL
                    END AS distance_bucket 
                    FROM {TABLE_CNG_STATIONS} 
                    WHERE ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 50000
                    ORDER BY distance_meters;
                """
        params = (
                    current_longitude, current_latitude,
                    current_longitude, current_latitude,
                    current_longitude, current_latitude,
                    current_longitude, current_latitude,
                    current_longitude, current_latitude,
                    current_longitude, current_latitude,
                    current_longitude, current_latitude
                )
        
    except Exception as e:
        return {"error": str(e)}, 500

    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        # print(rows)
        # name,latitude,longitude,phone,address,
        # Group results
        grouped = defaultdict(list)
        for row in rows:
            bucket = row[6]
            if bucket:
                grouped[bucket].append({
                    "name": row[0],
                    "latitude": row[1],
                    "longitude": row[2],
                    "phone": row[3],
                    "address": row[4],
					"distance_meters": row[5]
                    })
        # print((grouped))        
        return jsonify(grouped),200

    except Exception as e:
        return {"error": str(e)}, 500