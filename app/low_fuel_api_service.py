from shapely.geometry import LineString
from flask import jsonify


def getNearbyFuelStations(routePoints,productType,cursor,TABLE_NAME):
    try:
        nearby_points = []
        line = LineString([(coord['longitude'],coord['latitude']) for coord in routePoints])
        # print("line.wkt =",line.wkt)
        cursor.execute(f"""Select distinct city, price,latitude, longitude, product,id from {TABLE_NAME} where product='{productType}' and ST_DWithin(location::geography, ST_SetSRID(ST_GeomFromText(%s),4326), 200)""", (line.wkt,))
        points = cursor.fetchall()
        # print('get_nearyby_points: completed')
        # print(points);
        
        for point in points:
            # point_gem= loads(point[4]);
            nearby_points.append({
                'city': point[0],
                'price': point[1],
                'latitude': point[2],
                'longitude': point[3],
                'product': point[4],
                'id': point[5]
            })
        return nearby_points;
    except Exception as e:
        print(f"Error in getNearbyFuelStations: {e}")
        return jsonify({"error": str(e)}), 500


def getProductByItsId(cursor,TABLE_NAME,id):
    try:
        products = []
        cursor.execute(f"""select id,city,latitude,longitude,price,product from {TABLE_NAME} where id= {id}""");
        records = cursor.fetchall()
        for record in records:
            products.append({
            'id': record[0],
            'city': record[1],
            'latitude': record[2],
            'longitude': record[3],
            'price': record[4],
            'product': record[5],
            });
        return products
    except Exception as e:
            return {'code': 400, "message": "Query error"}
    



