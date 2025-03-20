import socketio
import tkinter as tk
from tkinter import font as tkfont
import customtkinter as ctk
import json

# Initialize Socket.IO client
socket = socketio.Client()

# Store logged-in user data
logged_in_user = None

# Tkinter Widgets
status_label = None
car_listbox = None  # Listbox for car selection
cars_data = []  # Stores car data received from the server

login_window = None
register_window = None

BACKGROUND_COLOR = "#F0F0F0"
TEXT_COLOR = "#333333"
BUTTON_COLOR = "#0078D7"
BUTTON_TEXT_COLOR = "#FFFFFF"
LISTBOX_BACKGROUND = "#FFFFFF"
LISTBOX_FOREGROUND = "#000000"
ERROR_COLOR = "#FF0000"
SUCCESS_COLOR = "#31E987"

FONT_STYLE = "Helvetica"
FONT_SIZE = 12

@socket.on('connect')
def on_connect():
    print("Mobile app connected to the server!")

@socket.on('server_response')
def on_server_response(data):
    print(f"Server response: {data['message']}")

    if status_label:
        message = data['message']
        if message == "car_rented":
            message = "Car rented!"
        elif message == "car_returned":
            message = "Car returned!"

        if "cars" in data and isinstance(data["cars"], list) and data["cars"]:
            global cars_data, car_listbox
            cars_data = data["cars"]

            car_listbox.delete(0, tk.END)
            for car in cars_data:
                car_listbox.insert(tk.END, f"{car['make']} {car['model']} (VIN: {car['vin']})")

            status_label.config(text="Select a car from the list.")
        else:
            status_label.config(text=message)

# Function to log in
def login(user_data):
    socket.emit('login', user_data)

# Query available cars
def query_available_cars():
    if logged_in_user:
        car_listbox.delete(0, tk.END)
        socket.emit('query_cars', {"user_id": logged_in_user["user_id"]})

# Rent a car
def rent_car():
    if logged_in_user and car_listbox.curselection():
        selected_index = car_listbox.curselection()[0]
        selected_car = cars_data[selected_index]
        socket.emit('start_rental', {"user_id": logged_in_user["user_id"], "vin": selected_car["vin"]})
        status_label.config(text=f"Renting {selected_car['make']} {selected_car['model']}...")

# Return a car
def return_car():
    if logged_in_user and car_listbox.curselection():
        selected_index = car_listbox.curselection()[0]
        selected_car = cars_data[selected_index]
        socket.emit('end_rental', {"user_id": logged_in_user["user_id"], "vin": selected_car["vin"]})
        status_label.config(text=f"Returning {selected_car['make']} {selected_car['model']}...")

# Connecting to the server
def connect_to_server():
    socket.connect('http://localhost:5000')

def open_register_window():
    global register_window, login_window, status_label

    register_window = tk.Toplevel()
    register_window.title("Register")
    register_window.geometry("500x650")
    register_window.configure(bg=BACKGROUND_COLOR)

    custom_font = tkfont.Font(family=FONT_STYLE, size=FONT_SIZE)

    tk.Label(register_window, text="Register", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 24, "bold")).pack(pady=10)

    # tk.Label(register_window, text="Name:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=custom_font).pack(pady=5)
    name_entry = ctk.CTkEntry(register_window, placeholder_text="Name", width=250, fg_color="#ffffff", text_color="#1C1C1B")
    name_entry.pack(pady=5)

    # tk.Label(register_window, text="Email:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=custom_font).pack(pady=5)
    email_entry = ctk.CTkEntry(register_window, placeholder_text="Email", width=250, fg_color="#ffffff", text_color="#1C1C1B")
    email_entry.pack(pady=5)

    # tk.Label(register_window, text="Password:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=custom_font).pack(pady=5)
    password_entry = ctk.CTkEntry(register_window, show="*", placeholder_text="Password", width=250, fg_color="#ffffff", text_color="#1C1C1B")
    password_entry.pack(pady=5)

    status_label = tk.Label(register_window, text="Status: Waiting...", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=custom_font)
    status_label.pack(pady=10)

    def handle_register():
        global status_label

        name = name_entry.get()
        email = email_entry.get()
        password = password_entry.get()

        try:
            with open("users.json", "r") as file:
                users = json.load(file)
        except FileNotFoundError:
            users = []

        if next((user for user in users if user['email'] == email), None):
            status_label.config(text="Email already registered!", fg=ERROR_COLOR)
            return
        elif not name or not email or not password:
            status_label.config(text="Please fill in all fields!", fg=ERROR_COLOR)
            return

        new_user = {
            "user_id": len(users) + 1,
            "name": name,
            "email": email,
            "password": password
        }

        users.append(new_user)

        with open("users.json", "w") as file:
            json.dump(users, file, indent=4)

        status_label.config(text="User registered successfully! Please log in.", fg=SUCCESS_COLOR)

        register_window.destroy()

    register_button = ctk.CTkButton(register_window, text="Register", command=handle_register, fg_color="#57B95C", text_color=BUTTON_TEXT_COLOR, width=200, height=30, corner_radius=8, border_width=0)
    register_button.pack(pady=10)

    back_button = ctk.CTkButton(register_window, text="Back to Login", command=lambda: register_window.destroy(), fg_color=BUTTON_COLOR, text_color=BUTTON_TEXT_COLOR, width=200, height=30, corner_radius=8, border_width=0)
    back_button.pack(pady=10)

# UI Setup for main window
def open_main_window():
    global status_label, car_listbox

    main_window = tk.Tk()
    main_window.title("CarSharing Mobile App")
    main_window.geometry("500x650")
    main_window.configure(bg=BACKGROUND_COLOR)

    custom_font = tkfont.Font(family=FONT_STYLE, size=FONT_SIZE)

    tk.Label(main_window, text=f"Welcome, {logged_in_user['name']}!", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 24, "bold")).pack(pady=10)

    # Car listbox
    car_listbox = tk.Listbox(main_window, bg=LISTBOX_BACKGROUND, fg=LISTBOX_FOREGROUND, font=custom_font, width=50, height=10)
    car_listbox.pack(pady=10)

    query_button = ctk.CTkButton(main_window, text="Search Cars", command=query_available_cars, fg_color=BUTTON_COLOR, text_color=BUTTON_TEXT_COLOR, width=200, height=30, corner_radius=8, border_width=0)
    query_button.pack(pady=10)

    rent_button = ctk.CTkButton(main_window, text="Rent Car", command=rent_car, fg_color="#57965C", text_color=BUTTON_TEXT_COLOR, width=200, height=30, corner_radius=8, border_width=0)
    rent_button.pack(pady=10)

    return_button = ctk.CTkButton(main_window, text="Return Car", command=return_car, fg_color="#C94F4F", text_color=BUTTON_TEXT_COLOR, width=200, height=30, corner_radius=8, border_width=0)
    return_button.pack(pady=10)

    # Status label
    status_label = tk.Label(main_window, text="Status: Waiting...", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=custom_font)
    status_label.pack(pady=20)

    main_window.mainloop()

# UI Setup for login window
def open_login_window():
    global login_window, status_label

    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("500x650")
    login_window.configure(bg=BACKGROUND_COLOR)

    custom_font = tkfont.Font(family=FONT_STYLE, size=FONT_SIZE)

    tk.Label(login_window, text="Log In", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 24, "bold")).pack(pady=10)

    # tk.Label(login_window, text="Email:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=custom_font).pack(pady=5)
    email_entry = ctk.CTkEntry(login_window, placeholder_text="Email", width=250, fg_color="#ffffff", text_color="#1C1C1B")
    email_entry.pack(pady=10)

    # tk.Label(login_window, text="Password:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=custom_font).pack(pady=5)
    password_entry = ctk.CTkEntry(login_window, show="*", placeholder_text="Password", width=250, fg_color="#ffffff", text_color="#1C1C1B")
    password_entry.pack(pady=10)

    status_label = tk.Label(login_window, text="Status: Waiting...", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=custom_font)
    status_label.pack(pady=10)

    def handle_login():
        global logged_in_user, status_label

        email = email_entry.get()
        password = password_entry.get()

        with open("users.json", "r") as file:
            users = json.load(file)

        user = next((user for user in users if user['email'] == email and user['password'] == password), None)

        if user:
            logged_in_user = {
                "user_id": user['user_id'],
                "name": user['name'],
                "email": email
            }
            login(logged_in_user)

            if login_window.winfo_exists():
                login_window.after_cancel(login_window.tk.call("after", "info"))
                login_window.quit()
                login_window.destroy()

            open_main_window()
        else:
            status_label.config(text="Invalid email or password!", fg=ERROR_COLOR)


    login_button = ctk.CTkButton(login_window, text="Login", command=handle_login, fg_color="#57B95C", text_color=BUTTON_TEXT_COLOR, width=200, height=30, corner_radius=8, border_width=0)
    login_button.pack(pady=10)

    register_button = ctk.CTkButton(login_window, text="Register", command=open_register_window, fg_color=BUTTON_COLOR, text_color=BUTTON_TEXT_COLOR, width=200, height=30, corner_radius=8, border_width=0)
    register_button.pack(pady=10)

    connect_to_server()
    login_window.mainloop()

open_login_window()