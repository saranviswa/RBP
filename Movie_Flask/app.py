from flask import Flask, request, jsonify 
from settings import DEBUG
from pymongo import MongoClient
from models import User, Movie, Ticket
import utils 
import os 
import logging
from flask_cors import CORS
from kafka import KafkaProducer, KafkaConsumer

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    filename='app.log',  
    filemode='a'  
)

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['DEBUG'] = DEBUG 

def get_mongo_db():
    PROD_MONGO_URI = os.environ.get('PROD_MONGO_URI')
    client = MongoClient(PROD_MONGO_URI)
    if PROD_MONGO_URI == "mongodb://localhost:27017/test":
        return client['test']
    return client['rbp']

db = get_mongo_db()

kafka_broker = 'localhost:9092'
topic = 'test_topic'
producer = KafkaProducer(bootstrap_servers=kafka_broker)
consumer = KafkaConsumer(topic, bootstrap_servers=kafka_broker, group_id='your_consumer_group_id')

import json

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    # Serialize the data to bytes
    value_bytes = json.dumps(data).encode('utf-8')
    producer.send(topic, value=value_bytes)
    return jsonify({"status": "success", "message": "Message sent to Kafka"}), 200


@app.route('/consume_message', methods=['GET'])
def consume_message():
    for message in consumer:
        data = message.value
        return jsonify({"status": "success", "data": data.decode()}), 200

@app.route('/api/v1.0/moviebooking/register', methods=['POST'])
def register_data():
    data = request.get_json()
    logging.info(f"Entered register user api, request body :::  {data}")
    required_fields=["first_name","last_name","email","login_id","password","confirm_password","contact_number","security_question","security_answer"]
    missing_fields= [field for field in required_fields if field not in data]
    if missing_fields:
        logging.warning(f"missing fields {missing_fields}")
        return utils.get_error_message(400, f"Missing fields {missing_fields}")
        
    if data['password'] != data['confirm_password']:
        logging.warning("Password and Confirm password fields does not match")
        return utils.get_error_message(400, "Password and Confirm password fields does not match")
    
    existing_user = db.users.find_one({'email':data['email']})
    if existing_user:
        logging.warning("Email already registered")
        return jsonify({'message': 'Email already registered'}), 409
    
    existing_user = db.users.find_one({'login_id':data['login_id']})

    if existing_user:
        logging.warning("Login ID already taken")
        return jsonify({'message': 'Login ID already taken'}), 409

    new_user = User()
    new_user.create_user(
        first_name = data['first_name'],
        last_name = data['last_name'],
        email = data['email'],
        login_id = data['login_id'],
        password = data['password'],
        contact_number = data['contact_number'],
        security_question = data['security_question'],
        security_answer = data['security_answer'],
        db = db
    )
    loggin.info("User registered successfully")
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/v1.0/moviebooking/login', methods=['POST'])
def login_user():
    data = request.get_json()
    logging.info(f"Entered login user api, request body ::: {data}")
    user = db.users.find_one({'login_id': data['login_id'], 'password': data['password']})
    if not user:
        logging.warning("Invalid login credentials")
        return jsonify({'message': 'Invalid login credentials'}), 401
    
    logging.info("Login successful")
    return jsonify({'message': 'Login successful!'})

@app.route('/api/v1.0/moviebooking/forgot', methods=['POST'])
def forgot_password():
    data = request.get_json()
    logging.info(f"Entered forgot password api, request body {data}")
    user = db.users.find_one({'email': data['email']})
    if user:
        return jsonify({'message': user['security_question']})
    logging.warning("User not registered")
    return jsonify({'message': 'User not registered'})

@app.route('/api/v1.0/moviebooking/resetpassword', methods=['POST'])
def reset_password():
    data = request.get_json()
    logging.info(f"Entered reset password {data}")
    user = db.users.find_one({'email': data['email']})
    if user['security_answer'] == data['security_answer']:
        return jsonify({'message': 'Invalid security question/answer'}), 400
    if data['password'] != data['confirm_password']:
        return jsonify({'message': 'Password and Confirm password fields does not match'})
    
    db.users.update_one(
        {'email': data['email']},
        {'$set': {'password': data['password']}}
    )

    return jsonify({'message': 'Password updated successfully!'}), 200



@app.route('/api/v1.0/moviebooking/all', methods=['GET'])
def get_all_movies():
    movies = list(db.movies.find({}, {'_id': False}))
    logging.info(f"response {movies}")
    return jsonify({'message': movies}), 200

@app.route('/api/v1.0/moviebooking/movies/search/<movie_name>', methods=['GET'])
def search_movies(movie_name):
    movies = list(db.movies.find({'movie_name': {'$regex': movie_name, '$options': 'i'}}, {'_id': False}))
    return jsonify({'movies': movies}), 200

@app.route('/api/v1.0/moviebooking/<movie_name>/add', methods=['POST'])
def book_tickets(movie_name):
    data = request.get_json()
    movie = db.movies.find_one({'movie_name': movie_name})
    if not movie:
        return jsonify({'message': 'Movie not found'}), 400
    if int(data['num_tickets']) <=0 or int(data['num_tickets']) > int(movie['available_tickets']):
        return jsonify({'message': 'invalid number of tickets'}), 400
    
    avail_tickets = int(movie['available_tickets'])
    seat_number = [] 
    for i in range(data['num_tickets']):
        seat_number.append(avail_tickets)
        avail_tickets = avail_tickets - 1

    new_ticket = Ticket()
    new_ticket.add_ticket(
        email=data['email'],
        movie_name= movie_name,
        theatre_name= data['theatre_name'],
        num_tickets= data['num_tickets'],
        seat_number= seat_number,
        db = db
    )
    db.movies.update_one(
        {'movie_name': movie_name, 'theatre_name' : data['theatre_name']},
        {'$set': {'available_tickets': avail_tickets}}
    )
    response = {
        'seat_number': seat_number,
        'movie_name': movie_name,
        'theatre_name': data['theatre_name'],
    }

    return jsonify({'message': 'Ticket booked', 'response': response}), 200

@app.route('/api/v1.0/moviebooking/bookedtickets/<email>')
def get_booked_tickets(email):
    tickets = db.tickets.find({'email': email})
    response = []
    for ticket in tickets:
        obj = {
            'movie_name': ticket['movie_name'],
            'theatre_name': ticket['theatre_name'],
            'seat_number': ticket['seat_number']
        }
        response.append(obj)
    
    return jsonify({'tickets': response})

@app.route('/api/v1.0/moviebooking/addmovies', methods=['POST'])
def add_new_movies():
    data = request.get_json()
    new_movie = Movie()
    new_movie.create_movie(
        movie_name = data['movie_name'],
        total_tickets_allotted = data['total_tickets_allotted'],
        theatre_name = data['theatre_name'],
        avail_tickets = data['available_tickets'],
        status = data['status'],
        db = db
    )
    return jsonify({'message': "New movie added"})

@app.route('/api/v1.0/moviebooking/deletemovies', methods=['DELETE'])
def delete_movies():
    data = request.get_json()
    db.movies.delete_one({'movie_name': data['movie_name'], 'theatre_name': data['theatre_name']})
    return jsonify({'message': "movie Deleted"})

if __name__ == '__main__':
    app.run()