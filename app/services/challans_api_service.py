import json
from flask import jsonify


def getTrafficFines(cursor, TABLE_CHALLAN):
    try:
        query = f"""
                    SELECT jsonb_object_agg(violationdescription, violation_data) AS result
                    FROM (
                        SELECT 
                            violationdescription,
                            jsonb_build_object(
                                '2w', jsonb_agg(jsonb_build_object(state, fine2wheeler)),
                                '3w', jsonb_agg(jsonb_build_object(state, fine3wheeler)),
                                'lmv', jsonb_agg(jsonb_build_object(state, finelmv)),
                                'mgv_hgv', jsonb_agg(jsonb_build_object(state, finemgvandhgv))
                            ) AS violation_data
                        FROM {TABLE_CHALLAN}
                        WHERE displayenabled = true
                        GROUP BY violationdescription
                    ) AS sub;
                    """
        
        cursor.execute(query)
        result = cursor.fetchone()[0]
        if not result:
            return jsonify({"message": "No fines found"}), 404  
        # result = json.loads(result)  # Convert JSONB to Python dict
        return jsonify(result), 200

    except Exception as e:
        print(f"Error in getTrafficFines: {e}")
        return jsonify({"error": str(e)}), 500    

