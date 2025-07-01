

def getUsers(cursor, TABLE_USERS_NAME,phone):
    cursor.execute(f"""Select * from {TABLE_USERS_NAME} where phone='{phone}'""")
    records= cursor.fetchall()
    users = []
    for rec in records:
        users.append({
                "id": rec[0],
                "name": rec[1],
                "phone": rec[2],
                "vehicle_type": rec[3],
                "fuel_type": rec[4],
                "email": rec[5],
                "created_date": rec[6]
        })
    return users;


def isUserRecordPresent(cursor, phone, TABLE_USERS_NAME):
    try:
        cursor.execute(f"""Select count(name) from {TABLE_USERS_NAME} where phone='{str(phone)}' """)
        cursor.connection.commit()
        record = cursor.fetchone()
        if(record[0]>0):
            return True  # user does exist
        else: 
            return False # user does not exist
    except Exception as e:
        print(f"Error checking user existence: {e}")
        return False  # in case of error, assume user does not exist

def addUser(cursor,data, TABLE):
    name = data.get('name')
    phone = str(data.get('phone'))
    vehicle_type = data.get('vehicle_type')
    fuel_type = data.get('fuel_type')
    email = data.get('email')

    # if isUserRecordPresent(cursor, phone, TABLE_USERS_NAME):
    user_record=getUsers(cursor, TABLE,phone)
    if len(user_record) > 0:
        return  {"code": 200, "message": "User already exists with this phone number.","phone": phone,"user": user_record[0]}
    else:
        try:
            cursor.execute(f"""INSERT INTO {TABLE} (name, phone,vehicle_type,fuel_type,email)
                            VALUES ('{name}', '{phone}','{vehicle_type}','{fuel_type}','{email}')""");
            cursor.connection.commit()
        except Exception as e:
            print(f"Error inserting user: {e}")
            return {"code": 500, "message": "Internal Server Error. User Data Not Saved."}
        if isUserRecordPresent(cursor, phone, TABLE):
            return {"code": 201, "message": "User Data Saved Successfully"}
        else:
            return {"code": 500, "message": "Internal Server Error. User Data Not Saved."}