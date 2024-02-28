from datetime import datetime
from flask import Flask, request
import sqlite3
from math import sqrt, pow

app = Flask(__name__)


def dist(x_1, y_1, x_2, y_2):
    return sqrt(pow((x_1 - x_2) * 111.32, 2) + pow((y_1 - y_2) * 111.32, 2))


def create_table():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (phoneNumber TEXT, latitude DOUBLE, longitude DOUBLE, datetime TEXT, UNIQUE(phoneNumber))''')

    connection.commit()
    connection.close()


def register_user(phone_number, latitude, longitude):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    current_datetime = datetime.now().replace(microsecond=0)

    cursor.execute('''INSERT OR IGNORE INTO Users (phoneNumber, latitude, longitude, datetime) VALUES (?, ?, ?, ?)''', (phone_number, latitude, longitude, current_datetime))
    cursor.execute('''UPDATE Users SET latitude = ?, longitude = ?, datetime = ? WHERE phoneNumber = ?''', (latitude, longitude, current_datetime, phone_number))

    connection.commit()
    connection.close()


def get_users():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()

    connection.close()
    return users


@app.route("/send-location", methods=["POST"])
def location():
    register_user(request.json["phoneNumber"], request.json["latitude"], request.json["longitude"])
    return "Success"


@app.route("/get-location")
def get_location():
    for user in get_users():
        if user[0] == request.args["phoneNumber"]:
            return [user[1], user[2]]
    return []


@app.route("/search")
def search():
    lst = []
    pos = []
    for user in get_users():
        if user[0] == request.args["phoneNumber"]:
            pos = [user[1], user[2]]
    for i in get_users():
        if dist(i[1], i[2], float(pos[0]), float(pos[1])) <= 6:
            lst.append(i[0])
    return lst


if __name__ == '__main__':
    create_table()
    app.run(debug=True)
