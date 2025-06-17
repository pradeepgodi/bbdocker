from flask import jsonify
from datetime import datetime
from collections import defaultdict


def deleteUserHistory(cursor,data, TABLE_HISTORY_NAME):
    phone=str(data.get('phone'))
    print(f"Deleting history for phone: {phone}")
    if not phone:
        return {"message": "Phone number is missing in the body"}, 400
    else:
        try:
            cursor.execute(f"""DELETE FROM {TABLE_HISTORY_NAME} WHERE phone = %s""", (phone,))
            record_count = cursor.rowcount
            cursor.connection.commit()
            if record_count == 0:
                print(f"No records found for phone = {phone}")
                return {"message": "No history found for the given phone number"}, 404
            else:
                print(f"Deleted {record_count} record(s) for phone = {phone}")
                return {"message": f"Deleted {record_count} record(s) for phone: {phone}"}, 200

        except Exception as e:
            print(f"Error deleting history for phone {phone}: {e}")
            return {"error": str(e)}, 500
    

def addUserHistory(cursor,data,TABLE_HISTORY_NAME,TABLE_USERS_NAME):
        price=data.get('price')
        phone=str(data.get('phone'))
        litres=data.get('litres')
        saved=data.get('saved')
        petrolBunkId = str(data.get('petrolBunkId'))
        product = str(data.get('product'))
        if not (price and phone and litres and saved and petrolBunkId and product):
            return {"message": "Few fields are missing in the body"}, 400
        else:
            current_date = datetime.now();
            creationDate=str(current_date.strftime("%x %X"))
            cursor.execute(f"""Select count(*) from {TABLE_USERS_NAME} where phone='{phone}' """)
            user_record = cursor.fetchone()
            if user_record[0] == 0:
                return {"message": "User not found"}, 404
            # Insert the history record
            try:
                cursor.execute(f"""SELECT max(id)+1 from history_new""")
                new_record_id=cursor.fetchone()[0]
                query = f"""INSERT INTO {TABLE_HISTORY_NAME} (id,phone,price, litres, saved, creationDate, petrolBunkId, product) VALUES ('{new_record_id}','{phone}',{price},{litres},{saved},'{creationDate}','{petrolBunkId}','{product}')"""
                cursor.execute(query)
                cursor.connection.commit()
                return {"message": "History added successfully"}, 201
            except Exception as e:
                return {"error": str(e)}, 500
      



def getUserHistory(cursor,phone,TABLE_HISTORY_NAME, TABLE_NAME):
        try:
            cursor.execute(f"""Select h.id, h.price, h.phone,h.litres, h.saved, h.creationDate, h.petrolBunkId,h.product, 
                                p.city from {TABLE_HISTORY_NAME} h  join {TABLE_NAME} p on CAST(h.petrolBunkId AS INTEGER)=p.id 
                                where h.phone='{phone}' """)
            records = cursor.fetchall()
            users = []
            for rec in records:
                users.append({
                    'id': rec[0],
                    'price': rec[1],
                    'phone': rec[2],
                    'litres': rec[3],
                    'saved': rec[4],
                    'creationDate': rec[5],
                    'petrolBunkId': rec[6],
                    'product': rec[7],
                    'city': rec[8],
                })
            return users
        except Exception as e:
            print(f"Error fetching user history: {e}")
            return {"error": str(e)}, 500
