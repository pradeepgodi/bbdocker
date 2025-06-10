import requests;
import json
import datetime

import psycopg2;
from shapely.geometry import Point, LineString
import polyline;
from flask import Flask,request, jsonify, render_template
import pandas,os

import os
from flask import Flask, request, jsonify
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required,get_jwt_identity, create_refresh_token,get_jwt)
from datetime import timedelta



import toll_plaza_api_service as toll
import weigh_bridges_nearby_api_service as nwb
import cng_api_service as cng
import ev_stations_api_service as ev
import token_api_service as token
import low_fuel_api_service as lowfuel
import users_api_service as user
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

## JWT Configuration
# Set the JWT access and refresh token expiration times
# You can adjust these values as per your requirements.
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", os.urandom(32).hex()) # REPLACE THIS IN PRODUCTION!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=int(os.environ.get("ACCESS_TOKEN_EXPIRY_HOURS"))) # Access tokens expire in 1 hour
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=int(os.environ.get("REFRESH_TOKEN_EXPIRY_DAYS"))) # Refresh tokens expire in 30 days
jwt = JWTManager(app)

# --- Blacklisting Mechanism (for token revocation) ---
# In a real production application, you would use a persistent store (like Redis, a database)
# to maintain this blacklist, so it survives server restarts.
# For this example, it's an in-memory set.
blacklist = set()
# This function will be called whenever a protected endpoint is accessed,
# to check if the JWT's unique identifier (jti) is in our blacklist.
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in blacklist

TABLE_NAME='BUNKSBUDDYPRODUCTS';
TABLE_USERS_NAME='Users_New';
TABLE_HISTORY_NAME='History_New';
TABLE_TOLL_PLAZA= 'toll_plaza';
TABLE_WEIGH_BRIDGE='test_weigh_bridge';
TABLE_WEIGH_BRIDGE_NEARBY='weigh_bridge_statewise';
TABLE_CNG_STATIONS= 'cng_stations';
TABLE_EV_STATIONS= 'ev_stations';
TABLE_VISHRAM_GHAR= 'vishram_ghar';

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

## Pradeep Godi - code starts here

@app.route('/',methods=['GET'])
def rootPage():
        # return "Welcome to BunksBuddy Apis!";
        # return render_template('index_1.html')
        return render_template('index.html')


# Login API and access token generation
@app.route("/login", methods=["POST"])
def getTokensAtLogin():
    """
    Authenticates a user using their mobile number.
    Assumes any pre-authentication (like OTP validation) is handled client-side.
    Expects JSON: {"phone": "..."}
    """
    phone = request.json.get("phone", None)
    access_token, refresh_token, user=token.get_tokens_at_login(phone, cursor, TABLE_USERS_NAME)
    if not user:
        return jsonify({"error": "User not found",'phone':phone}), 404
    else:
        return jsonify(
                code=200,
                message="Logged in Successfully",
                access_token=access_token,
                refresh_token=refresh_token,
                user=user
            ), 200

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True) # This decorator ensures a valid refresh token is present
def refresh_token():
    try:
        current_user_identity = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_identity)
        new_refresh_token = create_refresh_token(identity=current_user_identity)
        return jsonify(access_token=new_access_token,refresh_token=new_refresh_token), 200
    except Exception as e:  
        print(f"Error in refreshing token: {e}")
        return jsonify({"error": "Failed to refresh token"}), 500



# Toll Plaza APIs
@app.route('/tollsAlongRouteByPoints',methods=['POST'])
@jwt_required()
def tollsAlongRouteByPoint():
    header_validation=True
    data = request.get_json()
    return toll.getTollsAlongRouteByPoint(header_validation,cursor, TABLE_TOLL_PLAZA,data)
    
@app.route('/tollVehicleTypes',methods=['GET'])
# @jwt_required()
def tollVehicleTypes():
    header_validation=True
    return toll.getTollVehicleTypes(header_validation)

# Weigh Bridge APIs
@app.route('/nearbyWeighBridges', methods=['POST'])
@jwt_required() 
def get_nearby_weigh_bridges():
    data = request.get_json()
    return nwb.get_nearby_weigh_bridges(True,cursor, TABLE_WEIGH_BRIDGE_NEARBY,data)

# CNG stations APIs
@app.route('/nearbyCNGStations',methods=['POST'])
@jwt_required() 
def getCNGStations():
     header_validation=True
     data = request.get_json()
     return cng.get_nearby_cng_stations(header_validation,cursor, TABLE_CNG_STATIONS,data)

@app.route('/cngAlongRouteByPoints',methods=['POST'])
@jwt_required() 
def cngAlongRoute():
    header_validation=True
    data = request.get_json()
    return cng.getCngAlongRouteByPoints(header_validation,cursor, TABLE_CNG_STATIONS,data)

# EV stations APIs
@app.route('/nearbyEVStations',methods=['POST'])
def getEVStations():    
    header_validation=True
    data = request.get_json()
    return ev.get_nearby_ev_stations(header_validation,cursor, TABLE_EV_STATIONS,data)
     
@app.route('/evAlongRouteByPoints',methods=['POST'])
def evStationsAlongRoute():
    header_validation=True
    data = request.get_json()
    return ev.getEVAlongRouteByPoints(header_validation,cursor, TABLE_EV_STATIONS,data)

# Low Fuel APIs Petrol and Diesel
@app.route('/getProductById',methods=['POST'])
@jwt_required()
def getProductById():
    item = request.get_json()
    id=item.get('id')
    products =lowfuel.getProductByItsId(cursor,TABLE_NAME,id)
    if products:
        return jsonify(products),200
    else:
        return jsonify({'id': id, "message": "Product Not Found"}),400

@app.route('/productsNearByPoints',methods=['POST'])
@jwt_required()
def productsNearByPoints():
    try:
        data = request.get_json()
        routePoints=data.get('points')
        productType=data.get('product')
    except Exception as e:
        print(str(e))
        return {"message": "Invalid request data"},400;
    nearbylocations=lowfuel.getNearbyFuelStations(routePoints,productType,cursor,TABLE_NAME)
    if nearbylocations:
        return jsonify(nearbylocations), 200    
    else:
        return jsonify({"message": "No nearby locations found"}), 404
    
# User data handling APIs
@app.route('/users',methods=['GET','POST'])
@jwt_required()
def userTable():
    data = request.get_json()
    if data:
        if request.method == 'GET':
            phone = data.get('phone')
            message = user.getUsers(cursor, TABLE_USERS_NAME,phone)
            if message:
                return jsonify(message), 200
            else:
                return jsonify({"message": "User not found"}), 404
        elif request.method == 'POST':    
            name = data.get('name')
            phone = data.get('phone')
            vehicle_number = data.get('vehicle_number')
            record= user.addUser(cursor,name,phone,vehicle_number, TABLE_USERS_NAME)

            try:
                current_user_identity = get_jwt_identity()
                new_access_token = create_access_token(identity=current_user_identity)
                new_refresh_token = create_refresh_token(identity=current_user_identity)
                return jsonify(access_token=new_access_token,refresh_token=new_refresh_token,message=record.get("message"),code=record.get('code', 200)), record.get('code', 200)
            except Exception as e:  
                print(f"Error in refreshing token: {e}")
                return jsonify({"error": "Failed to refresh token"}), 500
    else:
        return {"message": "Body can't be empty"},400;


@app.route('/nearbyVishramGhars',methods=['POST'])
@jwt_required()
def nearby_vishram_ghars():
    data = request.get_json()
    return ghar.getNearbyVishramGhars(True,cursor, TABLE_VISHRAM_GHAR,data)

@app.route('/vishramGharAlongRouteByPoints',methods=['POST'])
@jwt_required()
def vishram_ghars_along_route():
    data = request.get_json()
    return ghar.getVishramGharAlongRouteByPoints(True,cursor, TABLE_VISHRAM_GHAR,data)

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
