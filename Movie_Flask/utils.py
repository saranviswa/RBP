from datetime import datetime
from flask import jsonify, make_response
import app
import pymongo
def get_error_message(code, message):
    return jsonify({'Status Code': f'{code}', 'Error Description': f'{message}', 'TimeOccured': datetime.now()}), code

def check_if_user_exists(json_data):
    login_id = json_data['LoginID']
    email_id = json_data['Email']
    query = {
        "$or": [
            {
                "LoginID": login_id
            },
            {
                "Email": email_id
            }
        ]
    }
    db = app.get_mongo_db()
    collection = db['User']

    if collection.count_documents(query) >0:
        return True
    
    return False

def add_user(json_data):
    db = database.get_db()
    collection = db['User']

    insert_result = collection.insert_one(json_data)

    if insert_result.inserted_id:
        return make_response(jsonify({'message':"User added. Please Login now"}), 200)
    
    else:
        return get_error_message(400, "Something went wrong, Please contact website admistrator")

