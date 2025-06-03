import requests;
import json
import datetime

import psycopg2;
from shapely.geometry import Point, LineString
import polyline;
from flask import Flask,request, jsonify, render_template
import pandas,os
import toll_plaza_api_service as toll
# import weigh_bridge_api_service as wb
import weigh_bridges_nearby_api_service as nwb
import cng_api_service as cng
import ev_stations_api_service as ev
import vishram_ghar_api_service as ghar


from urllib.request import urlopen 
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
# PROD Database
# connection = psycopg2.connect(dbname="postgis_test",host="localhost", port=5432, user="ramesh", password="123ramesh"); #user="Ramesh", password="123ramesh"
# Local Database
# connection = psycopg2.connect(dbname="postgis_test",host="localhost", port=5432); #user="Ramesh", password="123ramesh"
# connection = psycopg2.connect(dbname="testdb",host="localhost", port=5432,user="postgres", password="Paddi_1984")

db_file_name = "database_config.json"
with open(file=db_file_name) as f:
    db_config = json.load(f)
connection = psycopg2.connect(dbname=db_config['db']['name'],
                              host=db_config['db']['host'],
                               port=db_config['db']['port'],
                                user=db_config['db']['user'],
                                  password=db_config['db']['password'])
cursor = connection.cursor()


TABLE_NAME='BUNKSBUDDYPRODUCTS';
TABLE_USERS_NAME='Users_New';
TABLE_HISTORY_NAME='History_New';
TABLE_TOLL_PLAZA= 'toll_plaza';
TABLE_WEIGH_BRIDGE='test_weigh_bridge';
TABLE_WEIGH_BRIDGE_NEARBY='weigh_bridge_statewise';
TABLE_CNG_STATIONS= 'cng_stations';
TABLE_EV_STATIONS= 'ev_stations';
TABLE_VISHRAM_GHAR= 'vishram_ghar';


# cursor.execute("""INSERT INTO BUNKSBUDDY (sensor_id, longitude, latitude, country, sensorTemp, sensorPressure, sensorTime, sensorLocation) VALUES ('F040520 BJI910J 2', 77.58133,12.9329, 'Goa', 0, 996, now(), ST_GeomFromText('POINT(77.58133 12.9329)',4326))""");
# connection.commit()
# cursor.execute('''delete FROM BUNKSBUDDY;''')
# connection.commit();
# cursor.execute('''CREATE TABLE IF NOT EXISTS BUNKSBUDDY(id integer, city varchar(100),latitude float,longitude float,price float,location geometry);''')
cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME}(id integer,product varchar(100), city varchar(100),latitude float,longitude float,price float,location geometry);''')
connection.commit();
#
cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_USERS_NAME}(id SERIAL primary key, name varchar(100), phone varchar(100),vehicle_number varchar(100), dob varchar(20), createdAt timestamp default current_timestamp, updatedAt timestamp default current_timestamp);''')
# CREATE TABLE IF NOT EXISTS Users_New(id SERIAL primary key, name varchar(100),phone varchar(100), vehicle_number varchar(100), dob varchar(20), createdAt timestamp default current_timestamp, updatedAt timestamp default current_timestamp)
connection.commit();
#===
# cursor.execute(f'''DROP TABLE IF EXISTS {TABLE_HISTORY_NAME};''')
# connection.commit();

cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_HISTORY_NAME}(id SERIAL primary key, phone varchar(100), price float, litres float, saved float, creationDate varchar(100), petrolBunkId varchar(100), product varchar(100));''')
connection.commit();

# cursor.execute(f'''select count(*) FROM {TABLE_NAME};''')
# # Fetch all rows from database
# record = cursor.fetchall()
# print("Data from Database:- ", record)

#Decode Polyline
def decode_polyline(encoded_polyline): 
    return polyline.decode(encoded_polyline)

#
def get_nearyby_points(encoded_poline, product):
    print('get_nearyby_points: called')
    coordinations = decode_polyline(encoded_poline)
    print("coordinations =",coordinations)
    line = LineString([(coord[1],coord[0]) for coord in coordinations])
    print("line =",line.wkt)
    
    cursor.execute(f"""Select city, price,latitude, longitude from {TABLE_NAME} where product='{product}' and ST_DWithin(location::geography, ST_SetSRID(ST_GeomFromText(%s),4326), 200)""", (line.wkt,))
    points = cursor.fetchall()
    print('get_nearyby_points: completed')
    print("Points :",points);
    nearby_points = []
    for point in points:
        # point_gem= loads(point[4]);
        nearby_points.append({
            'city': point[0],
            'price': point[1],
            'latitude': point[2],
            'longitude': point[3]
        })
    return nearby_points;

## Example Usage 
# polyline_str="g~|mAmooxMA{AT?C`D?z@xFE|C@lABlDAdIA`GCpECvBA"
# nearby_points=get_nearyby_points(polyline_str)
# for point in nearby_points:
#     print(f"Near by: ID={point['country']}")
##

## Pradeep Godi - code starts here
@app.route('/tollCount',methods=['GET'])
def tollCount():
    """
    Handles the '/tollCount' endpoint.
    Validates the request header and returns the toll count by querying the database.
    Returns:
        JSON response containing the toll count or an error message.
    """
     # Validates the request header
    header_validation=checkHeader(request)
     # Returns the toll count by passing the header validation result, database cursor, and table name
    return toll.getTollCount(header_validation,cursor, TABLE_TOLL_PLAZA)

@app.route('/stateWiseTollCount', methods=['GET'])
def getStateWiseTollCount():
    """
    Handles the '/stateWiseTollCount' endpoint.
    Validates the request header and retrieves state-wise toll count data from the database.
    Returns:
        JSON response containing state-wise toll count or an error message.
    """
    header_validation=checkHeader(request)
    return toll.getStateWiseTollCount(header_validation,cursor, TABLE_TOLL_PLAZA)


@app.route('/tollsAlongRouteByPoints',methods=['POST'])
def tollsAlongRouteByPoint():
    """
    Handles the '/tollsAlongRouteByPoints' POST route.
    This endpoint processes a request to retrieve tolls along a route based on 
    provided geographical points. It validates the request headers, extracts 
    the JSON payload, and delegates the processing to the `getTollsAlongRouteByPoint` 
    method of the `toll` object.
    Returns:
        Response: The response from the `getTollsAlongRouteByPoint` method, 
        which contains the toll information for the specified route.
    Request Body:
        JSON object containing the necessary data to identify the route.
    Dependencies:
        - `checkHeader(request)`: Validates the request headers.
        - `toll.getTollsAlongRouteByPoint(header_validation, cursor, TABLE_TOLL_PLAZA, data)`: 
        Retrieves toll information based on the provided data.
    """
    header_validation=checkHeader(request)
    data = request.get_json()
    return toll.getTollsAlongRouteByPoint(header_validation,cursor, TABLE_TOLL_PLAZA,data)
    
@app.route('/tollVehicleTypes',methods=['GET'])
def tollVehicleTypes():
    """
    Handles the '/tollVehilceTypes' endpoint.
    Validates the request header and retrieves vehicle types from the database.
    Returns:
        JSON response containing vehicle types or an error message.
    """
    header_validation=checkHeader(request)
    return toll.getTollVehicleTypes(header_validation)

# Weight Bridge APIs
# @app.route('/weightBridgeCount',methods=['GET'])
# def weightBridgeCount():    
#     """
#     Handles the '/weightBridgeCount' endpoint.
#     Validates the request header and returns the weight bridge count by querying the database.
#     Returns:
#         JSON response containing the weight bridge count or an error message.
#     """
#     header_validation=checkHeader(request)
#     return wb.getWeightBridgeCount(header_validation,cursor, TABLE_WEIGH_BRIDGE)

# @app.route('/weighBridgeAlongRoute',methods=['POST'])
# def getWeighBridges():
#     """
#     Handles the '/weighBridgeAlongRoute' POST route.
#     This endpoint processes a request to retrieve weigh bridges along a route based on 
#     provided geographical points. It validates the request headers, extracts 
#     the JSON payload, and delegates the processing to the `getWeighBridgeAlongRoute` 
#     method of the `wb` object.
#     Returns:
#         Response: The response from the `getWeighBridgeAlongRoute` method, 
#         which contains the weigh bridge information for the specified route.
#     Request Body:
#         JSON object containing the necessary data to identify the route.
#     Dependencies:
#         - `checkHeader(request)`: Validates the request headers.
#         - `wb.getWeighBridgeAlongRoute(header_validation,cursor, TABLE_WEIGH_BRIDGE,data)`: 
#         Retrieves weigh bridge information based on the provided data.
#     """
#     header_validation=checkHeader(request)
#     data = request.get_json()
#     return wb.getWeighBridgeAlongRoute(header_validation,cursor, TABLE_WEIGH_BRIDGE,data)




# @app.route('/weighBridgeNearMe',methods=['POST'])
# def getWeighBridgeNearMe():
#     """
#     this API uses Google Places API to get the weigh bridges near the user location which is time consuming,
#     hence not recomended to use in production. Use /nearbyWeighBridges instead.

#     Handles the '/weighBridgeNearMe' POST route.
#     This endpoint processes a request to retrieve weigh bridges near the user's location.
#     It validates the request headers, extracts the JSON payload, and delegates the processing 
#     to the `getWeighBridgeNearMe` method of the `wb` object.
#     Returns:
#         Response: The response from the `getWeighBridgeNearMe` method, 
#         which contains the weigh bridge information for the specified location.
#     Request Body:
#         JSON object containing the necessary data to identify the user's location.
#     Dependencies:
#         - `checkHeader(request)`: Validates the request headers.
#         - `wb.getWeighBridgeNearMe(header_validation,cursor, TABLE_WEIGH_BRIDGE,data)`: 
#         Retrieves weigh bridge information based on the provided data.
#     """
#     header_validation=checkHeader(request)
#     data = request.get_json()
#     return wb.getWeighBridgeNearMe(header_validation,cursor, TABLE_WEIGH_BRIDGE,data)


@app.route('/nearbyWeighBridges', methods=['POST'])
def get_nearby_weigh_bridges():
     
    """
    Handles the '/nearbyWeighBridges' GET route.
    This endpoint processes a request to retrieve nearby weigh bridges based on the user's location.
    It validates the request headers and delegates the processing to the `get_nearby_weigh_bridges` method of the `wb` object.
    Returns:
        Response: The response from the `get_nearby_weigh_bridges` method, 
        which contains the nearby weigh bridge information for the specified location.
    Dependencies:
        - `checkHeader(request)`: Validates the request headers.
        - `wb.get_nearby_weigh_bridges(header_validation,cursor, TABLE_WEIGH_BRIDGE,data)`: 
        Retrieves nearby weigh bridge information based on the provided data.
    """
    header_validation=checkHeader(request)
    data = request.get_json()
    return nwb.get_nearby_weigh_bridges(header_validation,cursor, TABLE_WEIGH_BRIDGE_NEARBY,data)




@app.route('/nearbyCNGStations',methods=['POST'])
def getCNGStations():
     header_validation=checkHeader(request)
     data = request.get_json()
     return cng.get_nearby_cng_stations(header_validation,cursor, TABLE_CNG_STATIONS,data)


@app.route('/cngAlongRouteByPoints',methods=['POST'])
def cngAlongRoute():
    header_validation=checkHeader(request)
    data = request.get_json()
    return cng.getCngAlongRouteByPoints(header_validation,cursor, TABLE_CNG_STATIONS,data)

@app.route('/nearbyEVStations',methods=['POST'])
def getEVStations():    
    header_validation=checkHeader(request)
    data = request.get_json()
    return ev.get_nearby_ev_stations(header_validation,cursor, TABLE_EV_STATIONS,data)
     
@app.route('/evAlongRouteByPoints',methods=['POST'])
def evStationsAlongRoute():
    header_validation=checkHeader(request)
    data = request.get_json()
    return ev.getEVAlongRouteByPoints(header_validation,cursor, TABLE_EV_STATIONS,data)



@app.route('/nearbyVishramGhars',methods=['POST'])
def nearby_vishram_ghars():
    header_validation=checkHeader(request)
    data = request.get_json()
    return ghar.getNearbyVishramGhars(header_validation,cursor, TABLE_VISHRAM_GHAR,data)

@app.route('/vishramGharAlongRouteByPoints',methods=['POST'])
def vishram_ghars_along_route():
    header_validation=checkHeader(request)
    data = request.get_json()
    return ghar.getVishramGharAlongRouteByPoints(header_validation,cursor, TABLE_VISHRAM_GHAR,data)

## Pradeep Godi - code ends here




@app.route('/deleteProduct',methods=['POST'])
def deleteProduct():
    if(checkHeader(request)==False):
         return {"message": "Token is not invalid"},401;
    item = request.get_json()
    id=item.get('id')
    try:
        cursor.execute(f"""delete from {TABLE_NAME} where id={id} """);
        connection.commit()
        return {'code': 200, "message": "Deleted Successfully."}
    except Exception as e:
        connection.rollback();
        print(str(e))   
        return {'code': 400, "message": "Failed to Delete."}

@app.route('/addProduct',methods=['POST'])
def addProducts():
    if(checkHeader(request)==False):
         return {"message": "Token is not invalid"},401;
    
    item = request.get_json()
    print(item);
    
    try:
        id=item.get('id')
        city=item.get('city')
        product=item.get('product')
        city = city.replace("'", "''")
        latitude=float(item.get('latitude'))
        longitude=float(item.get('longitude'))
        price=float(item.get('price'))

        cursor.execute(f"""INSERT INTO {TABLE_NAME} (id, product, longitude, latitude, city, price,  location) VALUES ({id},'{product}', {longitude},{latitude}, '{city}', {price}, ST_GeomFromText('POINT({longitude} {latitude})',4326))""");
        connection.commit()

        return {'city': city, "id": id, 'code': 200, "message": "Saved Successfully"}
    except Exception as e:
                    connection.rollback();
                    print(str(e))   
                    return {'code': 400, "message": "Failed to save"}
    # except Exception as e:
    #          print(str(e))
    #         #  connection.rollback();
    #          return str(e);
    return {'city': 'test'}

@app.route('/getProductById',methods=['POST'])
def getProductById():
    if(checkHeader(request)==False):
         return {"message": "Token is not invalid"},401;
    # data1 = request.get_data()
    item = request.get_json()
    print(item);
    
    try:
                            products = []
                            id=item.get('id')
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
                            # connection.commit()

                            return products;
    except Exception as e:
            connection.rollback();
            print(str(e))   
            return {'code': 400, "message": "Failed to save"}

def call(url,product):
    with app.app_context():
        try:
            r = requests.get(url)
            # print(r);
            res =r.text;
            # print(json.loads(res));
            # print(json.loads(res).get('data'));

            list=json.loads(res).get('data');
            id=100
            cursor.execute(f'''delete FROM {TABLE_NAME} where product='{product}';''')
            connection.commit();
            for item in list:
                try:
                    id=id+1;
                    # cursor = connection.cursor()
                    city=item.get('nama_lokasi')
                    city = city.replace("'", "''")
                    latitude=float(item.get('latitude'))
                    longitude=float(item.get('longitude'))
                    price=float(item.get('price'))
                    # print(latitude)
                    cursor.execute(f"""INSERT INTO {TABLE_NAME} (id, product, longitude, latitude, city, price,  location) VALUES ({id},'{product}', {longitude},{latitude}, '{city}', {price}, ST_GeomFromText('POINT({longitude} {latitude})',4326))""");
                    connection.commit()
                except Exception as e:
                    connection.rollback();
                    print(str(e))
                    
                    
            print("Total Count ", id);
            return r.text;
        except Exception as e:
            print(str(e))
            connection.rollback();
            return str(e);

#call('https://sasthamutton.com/JsonDisplayMarker.php?product=petrol');

@app.route('/',methods=['GET'])
def rootPage():
        # return "Welcome to BunksBuddy Apis!";
        # return render_template('index_1.html')
        return render_template('index.html')

@app.route('/loadPetrol',methods=['GET'])
def loadPetrol():
    if(checkHeader(request)==False):
         return {"message": "Token is not invalid"},401;
    call('https://sasthamutton.com/JsonDisplayMarker.php?product=petrol','petrol');
    return "Petrol Data loaded.";

@app.route('/loadDiesel',methods=['GET'])
def loadDiesel():
    if(checkHeader(request)==False):
         return {"message": "Token is not invalid"},401;
    call('https://sasthamutton.com/JsonDisplayMarker.php?product=diesel','diesel');
    return "Diesel Data loaded. ";

@app.route('/getPetrolData',methods=['GET'])
def getPetrolData():
    if(checkHeader(request)==False):
         return {"message": "Token is not invalid"},401;
    cursor.execute(f'''select count(*) FROM {TABLE_NAME};''')
    # Fetch all rows from database
    records = cursor.fetchall()
    print(records[0][0]);
    return {"total": str(records[0][0])} ;



@app.route('/productsNearBy',methods=['POST'])
def productsNearBy():
    if(checkHeader(request)==False):
         return {"message": "Token is not invalid"},401;
    # data1 = request.get_data()
    data1 = request.get_json()
    # data=data1.decode("utf-8")
    print(data1);
    polyline_str=data1.get('polyline')
    product=data1.get('product')

    print("polyline_str=",polyline_str);
    nearby_points = get_nearyby_points(polyline_str, product)
    return jsonify(nearby_points)
    # return jsonify({'test':})

@app.route('/getProducts',methods=['GET'])
def getProducts():
    if(checkHeader(request)==False):
         return {"message": "Token is not invalid"},401;
    return jsonify([{
        "id":1,
        "name": "Petrol"
    }, {
        "id":2,
        "name": "Diesel"
    }]);


@app.route('/productsNearByPoints',methods=['POST'])
def productsNearByPoints():
    if(checkHeader(request)==False):
         return {"message": "Token is not invalid"},401;
    nearby_points = []
    try:
        # data1 = request.get_data()
        data1 = request.get_json()
        # data=data1.decode("utf-8")
        # print(data1);
        points=data1.get('points')
        product=data1.get('product')

        print('productsNearByPoints: called')
        coordinations = points
        line = LineString([(coord['longitude'],coord['latitude']) for coord in coordinations])
        print("line.wkt =",line.wkt)
        
        cursor.execute(f"""Select distinct city, price,latitude, longitude, product,id from {TABLE_NAME} where product='{product}' and ST_DWithin(location::geography, ST_SetSRID(ST_GeomFromText(%s),4326), 200)""", (line.wkt,))
        points = cursor.fetchall()
        print('get_nearyby_points: completed')
        print(points);
       
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
             #=== TODO: Email to my,hareesh - : 
             cursor.execute("ROLLBACK")
             connection.commit()
             return {"message": "Internal Server."},500;
            

@app.route('/nearby',methods=['POST','GET'])
def nearBy():
    if(checkHeader(request)==False):
         return {"message": "Token is not invalid"},401;
    # data1 = request.get_data()
    data1 = request.get_json()
    # data=data1.decode("utf-8")
    # print(data1);
    polyline_str=data1.get('polyline')

    # print(polyline_str);
    nearby_points = get_nearyby_points(polyline_str, 'petrol')
    return jsonify(nearby_points)
    # return jsonify({'test':})

@app.route('/users',methods=['GET','POST'])
def userTable():
    if(checkHeader(request)==False):
         return {"message": "Token is not invalid"},401;
    try:
        if request.method == 'GET':
            cursor.execute(f"""Select id, name, phone,vehicle_number, createdAt from {TABLE_USERS_NAME} """)
            points = cursor.fetchall()
            print('get_nearyby_points: completed')
            print(points);
            users = []
            for point in points:
                users.append({
                    'id': point[0],
                    'name': point[1],
                    'phone': point[2],
                    'vehicle_number': point[3],
                    'createdAt': point[4]
                })
            return users;
        if request.method == 'POST':
            data1 = request.get_json()
            name=data1.get('name')
            phone=data1.get('phone')
            vehicle_number=data1.get('vehicle_number')
            #===
            cursor.execute(f"""Select  count(name) from {TABLE_USERS_NAME} where phone='{phone}' """)
            record = cursor.fetchone()
            print(record[0]);
            if(record[0]!=0):
                return {"code": 400, "message": "User is Already Exists."}
            #==
            cursor.execute(f"""INSERT INTO {TABLE_USERS_NAME} (name, phone, vehicle_number) VALUES ('{name}', '{phone}','{vehicle_number}')""");
            connection.commit();
            cursor.execute(f"""Select  * from {TABLE_USERS_NAME} where phone='{phone}' """)
            record = cursor.fetchone()
            if(record):
                if(record[0]!=0):
                    return {"code": 200, "message": "Logged in Successfully", "user":{
                        "id": record[0],
                        "name": record[1],
                        "phone": record[2],
                    }}; 
            return {"code": 200, "message": "User Data Saved Successfully"};
    except Exception as e:
             #=== TODO: Email to my,hareesh - : 
             print(e)
             cursor.execute("ROLLBACK")
             connection.commit()
             return {"message": "Internal Server."},500;

@app.route('/health',methods=['GET'])
def health():
    if request.method == 'GET':
        if(checkHeader(request)==True):
            return {"message": "ok"};
    
        return  {"message": "failed"},401;

def checkHeader(request): 
        try : 
            headers = request.headers
            bearer = headers.get('Authorization')    # Bearer YourTokenHere
            token = bearer.split()[1] 
            if(token=="8efJqo4xHEu7oMpTMyIufaQyHS"):
                return True
        except Exception as e:
            return False
        return False
    
#id SERIAL primary key, phone varchar(100), price float, litres float, saved float     
@app.route('/history',methods=['GET','POST'])
def historyTable():
    if request.method == 'GET':
        phone = request.args.get("phone");
        cursor.execute(f"""Select h.id, h.price, h.phone,h.litres, h.saved, h.creationDate, h.petrolBunkId,h.product, p.city from {TABLE_HISTORY_NAME} h  join {TABLE_NAME} p on CAST(h.petrolBunkId AS INTEGER)=p.id where h.phone='{phone}'""")

        points = cursor.fetchall()
        print('historyTable: completed')
        print(points);
        users = []
        for point in points:
            users.append({
                'id': point[0],
                'price': point[1],
                'phone': point[2],
                'litres': point[3],
                'saved': point[4],
                'creationDate': point[5],
                'petrolBunkId': point[6],
                'product': point[7],
                'city': point[8],
            })
        return users;
    if request.method == 'POST':
        data1 = request.get_json()
        price=data1.get('price')
        phone=data1.get('phone')
        litres=data1.get('litres')
        saved=data1.get('saved')
        petrolBunkId = data1.get('petrolBunkId')
        product = data1.get('product')
        
        x = datetime.datetime.now();
        creationDate=x.strftime("%x %X");
        #===
        cursor.execute(f"""Select  count(name) from {TABLE_USERS_NAME} where phone='{phone}' """)
        record = cursor.fetchone()
        print(record[0]);
        if(record[0]!=0):
            cursor.execute(f"""INSERT INTO {TABLE_HISTORY_NAME} (phone, price, litres,saved,creationDate, petrolBunkId,product) VALUES ('{phone}',{price},{litres},{saved}, '{creationDate}', '{petrolBunkId}','{product}' )""");
            connection.commit();
            return {"code": 200, "message": "History Saved Successy"};    
        #==
        
        return {"code": 400, "message": "User is not Exists."},400

@app.route('/login', methods=['GET','POST'])
def loginApi():
    if request.method == 'GET':
        phone = request.args.get("phone");
        
  
    if request.method == 'POST':
        try:
            data1 = request.get_json()
            phone=data1.get('phone')
            cursor.execute(f"""Select  * from {TABLE_USERS_NAME} where phone='{phone}' """)
            record = cursor.fetchone()
            print(record[0]);
            
            if(record[0]!=0):
                return {"code": 200, "message": "Logged in Successy", "user":{
                    "id": record[0],
                    "name": record[1],
                    "phone": record[2],
                }}; 
            else :  
                return {"code": 400, "message": "User is not found."}; 
        except Exception as e:
                print(str(e)) 
        return {"code": 400, "message": "User is not found."}; 


@app.route('/deleteHistory',methods=['POST'])
def deleteHistory():
    if(checkHeader(request)==False):
         return {"message": "Token is not invalid"},401;
    if request.method == 'POST':
        data1 = request.get_json()
        phone=data1.get('phone')
        cursor.execute(f'''delete FROM {TABLE_HISTORY_NAME} where phone='{phone}';''')
        connection.commit();
        return {"code": 200, "message": "History Deleted Successfully"}

    return {"code": 400, "message": "History Deleted Failed"},400

    
#Root endpoint
@app.get('/upload')
def upload():
    return render_template('upload-excel.html')

@app.post('/view')
def view():
 
    # Read the File using Flask request
    file = request.files['file']
    # save file in local directory
    file.save(file.filename)
 
    # Parse the data as a Pandas DataFrame type
    data = pandas.read_excel(file)
    records=data.to_json(orient='records')
    # print(records);
    data = [];
    # print(records)
    temp=json.loads(records);
    result = dumpData(temp);
    if(result):
        return result;
    # Return HTML snippet that will render the table
    # return data.to_html()
    return data;

def dumpData(list):
    with app.app_context():
        total=0;
        try:
            cursor.execute(f'''delete FROM {TABLE_NAME};''')
            
            connection.commit();
            for item in list:
                try:
                    id=item.get('id');
                    # cursor = connection.cursor()
                    city=str(item.get('farmname'))
                    city = city.replace("'", "''")
                    latitude=float(item.get('latitude'))
                    longitude=float(item.get('longitude'))
                    price=float(item.get('price'))
                    product=item.get('product')
                    # print(latitude)
                    cursor.execute(f"""INSERT INTO {TABLE_NAME} (id, product, longitude, latitude, city, price,  location) VALUES ({id},'{product}', {longitude},{latitude}, '{city}', {price}, ST_GeomFromText('POINT({longitude} {latitude})',4326))""");
                    connection.commit()
                    total=total+1
                except Exception as e:
                    connection.rollback();
                    print(str(e))
                    print(item.get('farmname'))
                    
                    
            # print("Total Count ", id);
        except Exception as e:
            print(str(e))
            connection.rollback();
            # return str(e);
    return f"""{total} Records Successfully Saved."""

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='127.0.0.1',debug=True)
     # Production
    # http_server = WSGIServer(('', 5000), app)
    # http_server.serve_forever()
