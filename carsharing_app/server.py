from flask import Flask, request, jsonify
import json
from flask_socketio import SocketIO, send, emit
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

USERS_DB = "users.json"
CARS_DB = "cars.json"

connected_users = {}
connected_cars = {}
rented_cars = {}  # Rental cars and their users

def load_db(file_name):
    try:
        with open(file_name, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    return data

def save_db(file_name, data):
    try:
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving the data to database!", e)

@app.route('/')
def homepage():
    return "The server is running!"

@socketio.on('connect_car')
def handle_connect_car(data):
    vin = data['vin']
    connected_cars[vin] = request.sid  # Asociază VIN-ul cu sesiunea socketului
    print(f"Car {vin} connected!")

@socketio.on('query_cars')
def handle_query_cars(data):
    user_id = data['user_id']
    print(f"Query for cars from {user_id}")

    # Load cars data
    cars = load_db(CARS_DB)

    # Filter available cars
    available_cars = [car for car in cars if car['available']]

    if available_cars:
        emit('server_response', {"message": "Available cars", "cars": available_cars, "user_id": user_id})
    else:
        emit('server_response', {"message": "No cars available at the moment. Try again later!", "user_id": user_id})

@socketio.on('start_rental')
def handle_start_rental(data):
    user_id = data['user_id']
    vin = data['vin']
    print(f"User {user_id} requested to rent car {vin}")

    cars = load_db(CARS_DB)

    car = next((car for car in cars if car['vin'] == vin), None)
    if not car or not car['available']:
        emit('server_response', {"message": "Car unavailable", "user_id": user_id})
        return

    if vin in connected_cars:
        emit('request_car_status', {"vin": vin}, room=connected_cars[vin])
        time.sleep(2)

        def check_car_status():
            time.sleep(1)
            if "status_code" in car and car["status_code"] == 0:
                car['available'] = False
                save_db(CARS_DB, cars)
                rented_cars[vin] = user_id
                socketio.emit('server_response', {"message": "car_rented", "user_id": user_id})
                socketio.emit('unlock_car', {"vin": vin})
                socketio.emit('start_rental_car', {"vin": vin}, room=connected_cars[vin])
                threading.Thread(target=monitor_rented_car, args=(vin,), daemon=True).start()
            else:
                socketio.emit('server_response', {"message": "Car is not in good condition", "user_id": user_id})

        threading.Thread(target=check_car_status, daemon=True).start()
    else:
        emit('server_response', {"message": "Car is offline", "user_id": user_id})

def monitor_rented_car(vin):
    while vin in rented_cars:
        if vin in connected_cars:
            socketio.emit('request_car_status', {"vin": vin}, room=connected_cars[vin])
        time.sleep(10)

@socketio.on('car_status_response')
def handle_car_status_response(data):
    vin = data["vin"]
    status_code = data["status_code"]
    status_message = data["status_message"]

    print(f"Received status from car {vin}: {status_message}")

    if vin in rented_cars and status_code != 0:
        user_id = rented_cars[vin]
        socketio.emit('server_response', {"message": f"Warning! {status_message}", "user_id": user_id})

@socketio.on('end_rental')
def handle_end_rental(data):
    user_id = data['user_id']
    vin = data['vin']

    if vin in rented_cars:
        cars = load_db(CARS_DB)

        for car in cars:
            if car['vin'] == vin:
                car['available'] = True
                break

        save_db(CARS_DB, cars)
        del rented_cars[vin]

        emit('lock_car', {"vin": vin})
        emit('server_response', {"message": "car_returned", "user_id": user_id})
        emit('end_rental_car', {"vin": vin}, room=connected_cars[vin])


@socketio.on('disconnect')
def handle_disconnect():
    for vin, sid in list(connected_cars.items()):
        if sid == request.sid:
            print(f"Car {vin} disconnected")
            del connected_cars[vin]

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
