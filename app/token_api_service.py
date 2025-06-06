from flask_jwt_extended import (JWTManager, create_access_token, jwt_required,get_jwt_identity, create_refresh_token,get_jwt)
from flask import Flask, jsonify, request


def get_tokens_at_login(phone, cursor, TABLE_USERS_NAME):
    if not phone:
        return jsonify({"msg": "Missing mobile number"}), 400
    try:
        phone = str(phone)
        cursor.execute(f"""Select  * from {TABLE_USERS_NAME} where phone='{phone}' """)
        record = cursor.fetchone()
        if record is None:
            user_record={}
            access_token = ''
            refresh_token = ''
        else:
            user_record = {
                "id": record[0],
                "name": record[1],
                "contact": record[2],
                "vehicle_number": record[3],
                "dob": record[4],
                "created_at": record[5],
                "updated_at": record[6]
            }
 
            access_token = create_access_token(identity=phone)
            refresh_token = create_refresh_token(identity=phone)
        return access_token, refresh_token, user_record
    except Exception as e:
        print(f"Error in generating the token: {e}")
        return jsonify({"msg": "Internal server error"}), 500




