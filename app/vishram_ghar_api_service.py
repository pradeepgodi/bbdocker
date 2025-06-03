from flask import jsonify
from collections import defaultdict
from shapely.geometry import LineString


def getNearbyVishramGhars(header_validation,cursor, TABLE_VISHRAM_GHAR,data):
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
                    omc,code,name,area,latitude,longitude,
                    ST_DistanceSphere(ST_MakePoint(longitude, latitude),ST_MakePoint(%s, %s)) AS distance_meters,
                    CASE
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 10000 THEN 'within_10_kms'
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 20000 THEN 'within_20_kms'
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 30000 THEN 'within_30_kms'
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 40000 THEN 'within_40_kms'
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 50000 THEN 'within_50_kms'
                        ELSE NULL
                    END AS distance_bucket 
                    FROM {TABLE_VISHRAM_GHAR} 
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
        grouped = defaultdict(list)
        for row in rows:
            bucket = row[7]
            if bucket:
                grouped[bucket].append({
                    "omc": row[0],
                    "code": row[1],
                    "name": row[2],
                    "area": row[3],
                    "latitude": row[4],
					"longitude": row[5],
                    "distance_meters": row[6]
                    })  
        return jsonify(grouped),200

    except Exception as e:
        return {"error": str(e)}, 500


def getVishramGharAlongRouteByPoints(header_validation,cursor, TABLE_VISHRAM_GHAR,data):
    if not header_validation:
        return {"message": "Token is not valid"}, 401
    
    try:
        threshold_toll_distance = data['distance_threshold']
    except KeyError:
        threshold_toll_distance = 1500

    try:    
        location_lines = LineString([(loc['longitude'], loc['latitude']) for loc in data['points']])
      
        # Query the data base for given vehicle type and location 
        cursor.execute(f'''SELECT omc,code,name,area,latitude,longitude
                         FROM {TABLE_VISHRAM_GHAR} WHERE ST_DWithin(location::geography, 
                         ST_SetSRID(ST_GeomFromText(%s),4326), {threshold_toll_distance})''', (location_lines.wkt,))

        nearby_wb = cursor.fetchall()

        nearby_wb_data=[]
        for data in nearby_wb:
            temp_dict = {"omc":data[0],"code":data[1],"name":data[2],"area":data[3],"latitude":data[4],"longitude":data[5]} 
            nearby_wb_data.append(temp_dict)
        return nearby_wb_data,200
    except Exception as e:
        print(str(e))
        return {"message": "Internal Server Error"}, 500  