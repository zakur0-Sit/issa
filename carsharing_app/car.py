import json
import socketio
import time
import threading

VIN = "VIN1234"
socket = socketio.Client()

rented = False

@socket.on('connect')
def on_connect():
    print(f"The car {VIN} connected to the server")
    socket.emit('connect_car', {"vin": VIN})

@socket.on('unlock_car')
def on_unlock_car(data):
    if data["vin"] == VIN:
        print(f"The car {VIN} was unlocked!")

@socket.on('lock_car')
def on_lock(data):
    if data["vin"] == VIN:
        print(f"The car {VIN} was locked!")

# Car status
def get_car_status():
    with open("cars.json", "r") as file:
        cars = json.load(file)
        car = next((car for car in cars if car['vin'] == VIN), None)
        if car:
            status_code = car.get("status_code", 0)  # Default la 0 dacă nu exista status_code
            status_codes = {
                0: "Car OK",
                1: "Engine problem",
                2: "Door open",
                3: "Low fuel",
                4: "Maintenance required"
            }
            status_message = status_codes.get(status_code, "Unknown status")
            return {"vin": VIN, "status_code": status_code, "status_message": status_message}
        else:
            return {"vin": VIN, "status_code": 0, "status_message": "Ready to go"}

@socket.on('request_car_status')
def on_request_car_status(data):
    if data["vin"] == VIN:
        status = get_car_status()
        print(f"Sending status: {status}")
        socket.emit('car_status_response', status)

# Interoghează statusul la fiecare 10 secunde
def periodic_status_update():
    global rented
    while rented:
        status = get_car_status()
        socket.emit('car_status_update', status)
        print(f"Periodic status update: {status}")
        time.sleep(10)

@socket.on('start_rental_car')
def on_start_rental(data):
    global rented
    if data["vin"] == VIN:
        rented = True
        threading.Thread(target=periodic_status_update, daemon=True).start()
        print(f"Car {VIN} is now rented!")

@socket.on('end_rental_car')
def on_end_rental(data):
    global rented
    if data["vin"] == VIN:
        rented = False
        print(f"Car {VIN} rental ended.")

socket.connect('http://localhost:5000')
socket.wait()
