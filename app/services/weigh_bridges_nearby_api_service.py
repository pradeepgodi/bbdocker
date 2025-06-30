from shapely.geometry import LineString
from collections import defaultdict
from flask import jsonify
import os

def getWeighBridgeAlongRoute(cursor, TABLE_WEIGH_BRIDGE,lat_long):
    THRESHOLD_DISTANCE=os.environ.get("THRESHOLD_DISTANCE") 
    try:    
        # location_lines = LineString([(loc['longitude'], loc['latitude']) for loc in data['points']])
        location_lines=LineString(lat_long)
      
        # Query the data base for given vehicle type and location 
        cursor.execute(f'''SELECT name,phone,city,formatted_address,latitude,longitude,capacity,length
                         FROM {TABLE_WEIGH_BRIDGE} WHERE ST_DWithin(location::geography, 
                         ST_SetSRID(ST_GeomFromText(%s),4326), {THRESHOLD_DISTANCE})''', (location_lines.wkt,))
        
        # Fetch all rows from database
        nearby_wb = cursor.fetchall()

        nearby_wb_data=[]
        for data in nearby_wb:
            temp_dict = {"name":data[0],"phone":data[1],"city":data[2],"address":data[3],"latitude":data[4],"longitude":data[5],"capacity":data[6],"length":data[7]} 
            nearby_wb_data.append(temp_dict)
        return nearby_wb_data,200
    except Exception as e:
        print(str(e))
        return {"message": "Internal Server Error"}, 500  

def get_nearby_weigh_bridges(cursor, TABLE_WEIGH_BRIDGE_NEARBY,data):
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
                    name,phone,city,formatted_address,latitude,longitude,capacity,length,
                    ST_DistanceSphere(ST_MakePoint(longitude, latitude),ST_MakePoint(%s, %s)) AS distance_meters,
                    CASE
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 10000 THEN 'within_10_kms'
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 20000 THEN 'within_20_kms'
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 30000 THEN 'within_30_kms'
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 40000 THEN 'within_40_kms'
                        WHEN ST_DistanceSphere(ST_MakePoint(longitude, latitude), ST_MakePoint(%s, %s)) <= 50000 THEN 'within_50_kms'
                        ELSE NULL
                    END AS distance_bucket 
                    FROM {TABLE_WEIGH_BRIDGE_NEARBY} 
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
    #  name,phone,city,formatted_address,latitude,longitude,capacity,length,distance_meters
        # Group results
        grouped = defaultdict(list)
        for row in rows:
            bucket = row[9]
            if bucket:
                grouped[bucket].append({
                    "name": row[0],
                    "phone": row[1],
                    "city": row[2],
                    "address": row[3],
                    "latitude": row[4],
                    "longitude": row[5],
					"capacity":row[6],
					"length":row[7],
					"distance_meters": row[8]
                    })
        return jsonify(grouped),200

    except Exception as e:
        return {"error": str(e)}, 500