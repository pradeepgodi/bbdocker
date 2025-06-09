

def getUsers(cursor, TABLE_USERS_NAME,phone):
    cursor.execute(f"""Select id, name, phone,vehicle_number, createdAt from {TABLE_USERS_NAME} where phone='{phone}'""")
    records= cursor.fetchall()
    users = []
    for rec in records:
        users.append({
            'id': rec[0],
            'name': rec[1],
            'phone': rec[2],
            'vehicle_number': rec[3],
            'createdAt': rec[4]
        })
    return users;


def checkUserExists(cursor, phone, TABLE_USERS_NAME):
    try:
        phone = str(phone)
        cursor.execute(f"""Select count(name) from {TABLE_USERS_NAME} where phone='{phone}' """)
        record = cursor.fetchone()
        if(record[0]>0):
            return True  # user does exist
        else: 
            return False # user does not exist
    except Exception as e:
        print(f"Error checking user existence: {e}")
        return False  # in case of error, assume user does not exist

def addUser(cursor,name,phone,vehicle_number, TABLE_USERS_NAME):
    if checkUserExists(cursor, phone, TABLE_USERS_NAME):
        return  {"code": 200, "message": "User already exists with this phone number.","phone": phone}
    else:
        cursor.execute(f"""INSERT INTO {TABLE_USERS_NAME} (name, phone, vehicle_number) VALUES ('{name}', '{phone}','{vehicle_number}')""");
        cursor.connection.commit();
        if checkUserExists(cursor, phone, TABLE_USERS_NAME):
            return {"code": 201, "message": "User Data Saved Successfully"}
        else:
            return {"code": 500, "message": "Internal Server Error. User Data Not Saved."}

