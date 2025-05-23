from shapely.geometry import LineString



def getTollVehicleTypes(header_validation):
    # This function retrieves the vehicle types associated with toll plazas from the database.
    if not header_validation:
        return {"message": "Token is not valid"}, 401
    else:
        return [
                {"id":1,"name": "Car/Jeep/Van","value":"car_jeep_van"}, 
                {"id":2,"name": "Bus/Truck","value":"bus_truck"},
                {"id":3,"name": "LCV","value":"lcv"},
                {"id":4,"name": "HCM/EME","value":"hcm_eme"},
                {"id":5,"name": "upto 3 Axle Vehicle","value":"upto_3_axle_vehicle"}, 
                {"id":6,"name": "4 to 6 Axle","value":"4_to_6_axle"}, 
                {"id":7,"name": "7 or more Axle","value":"7_or_more_axle"}], 200

def getTollsAlongRouteByPoint(header_validation, cursor, TABLE_TOLL_PLAZA, data):
    # This function retrieves toll plaza information along a route based on given points.
    # It takes four parameters: header_validation for validating the request headers,
    # cursor for executing database queries, TABLE_TOLL_PLAZA as the name of the table containing toll plaza data,
    # and data which includes the input points to determine the route.
    if not header_validation:
        return {"message": "Token is not valid"}, 401
    try:
        vehicle_type=data['vehicle_type']
        try:
            threshold_toll_distance = data['distance_threshold']
        except KeyError:
            threshold_toll_distance = 1500
        # Default distance threshold is set to 1000 meters if not provided in the request body.

        """
        Valid Vehicle type (any one) that should be passed in the request body:
            car_jeep_van,4_to_6_axle,7_or_more_axle, bus_truck, hcm_eme,lcv,upto_3_axle_vehicle"""
        
        location_lines = LineString([(loc['longitude'], loc['latitude']) for loc in data['points']])

        # select the coulmn name for Single Journey price in the table based on vehicle type
        query_car_jeep_van = "car_jeep_van_single_journey" 
        query_4_to_6_axle = "_4_to_6_axle_single_journey"
        query_7_or_more_axle = "_7_or_more_axle_single_journey" 
        query_lcv = "lcv_single_journey"
        query_bus_truck = "bus_truck_single_journey" 
        query_upto_3_axle_vehicle = "upto_3_axle_vehicle_single_journey"
        query_hcm_eme = "hcm_eme_single_journey"

        # Select the query based on vehicle type
        if vehicle_type == "car_jeep_van":
            query = query_car_jeep_van
        elif vehicle_type == "4_to_6_axle":
            query = query_4_to_6_axle
        elif vehicle_type == "7_or_more_axle":
            query = query_7_or_more_axle
        elif vehicle_type == "lcv": 
            query = query_lcv
        elif vehicle_type == "bus_truck":
            query = query_bus_truck  
        elif vehicle_type == "upto_3_axle_vehicle":
            query = query_upto_3_axle_vehicle
        elif vehicle_type == "hcm_eme":
            query = query_hcm_eme
        else:
            return {"message": "Invalid vehicle type" , "vehicle_type": vehicle_type}, 400
        
        # Query the data base for given vehicle type and location 
        cursor.execute(f'''SELECT toll_plaza_id,toll_plaza_name,latitude,longitude,{query}
                         FROM {TABLE_TOLL_PLAZA} WHERE ST_DWithin(location::geography, 
                         ST_SetSRID(ST_GeomFromText(%s),4326), {threshold_toll_distance})''', (location_lines.wkt,))
        
        # Fetch all rows from database
        nearby_tolls = cursor.fetchall()
        nearby_tolls_data=[]
        for data in nearby_tolls:
            temp_dict = {"toll_plaza_name":data[1],"toll_plaza_id":int(data[0]),"latitude":data[2],"longitude":data[3],"toll_fee":data[4] }
            nearby_tolls_data.append(temp_dict)
        # print(nearby_tolls_data)
        return nearby_tolls_data,200
        # return {vehicle_type :nearby_tolls_data},200
    except Exception as e:
        print(str(e))
        return {"message": "Internal Server Error"}, 500   
        

def getTollCount(header_validation, cursor, TABLE_TOLL_PLAZA):
    # Retrieves the count of toll plaza records from the database
    # Parameters:
    # header_validation: An object or function to validate request headers (not used in this snippet)
    # cursor: A database cursor object used to execute SQL queries
    # TABLE_TOLL_PLAZA: A string representing the name of the toll plaza table in the database
    if not header_validation:
        return {"message": "Token is not valid"}, 401
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {TABLE_TOLL_PLAZA};')
        count = cursor.fetchone()[0]
        return {"totalCount": count}, 200  # Return the count as an integer, not a string
    except Exception as e:
        print(f"Error in getTollCount: {str(e)}")  # Improved logging
        return {"message": "Internal Server Error"}, 500


def getStateWiseTollCount(header_validation, cursor, TABLE_TOLL_PLAZA):
    # This function retrieves the count of toll plazas state-wise from the database.
    # It takes three parameters: header_validation, cursor, and TABLE_TOLL_PLAZA.
    # header_validation is presumably used to validate the headers of the incoming request.
    # cursor is a database cursor object used to execute SQL queries.
    # TABLE_TOLL_PLAZA is the name of the table from which the toll plaza data is fetched.
    if not header_validation:
        return {"message": "Token is not valid"}, 401
    try:
        cursor.execute(f'''SELECT state, count(*) FROM {TABLE_TOLL_PLAZA} GROUP BY state ORDER BY 2 DESC;''')
        # Fetch all rows from database  
        records = cursor.fetchall()
        state_wise_toll_count = {}
        for record in records:
            state_wise_toll_count[record[0]] = record[1]
        return {"stateWiseTollCount": state_wise_toll_count}, 200
    except Exception as e:
        print(str(e))
        return {"message": "Internal Server Error"}, 500





