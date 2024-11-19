from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from database.connect import engine
from gens import calculate_day_degrees

app = Flask(__name__)

session = Session(bind=engine)


@app.route('/')
def hello_world():
    return 'Hello, Docker with Gunicorn and Reloading'


@app.route('/stationID/<string:stationID>/pestID/<string:pestID>/modelID/<string:modelID>', methods=['GET'])
def fetch_station_data(stationID, pestID, modelID):
    return f"{calculate_day_degrees(stationID, pestID)}"


if __name__ == '__main__':
    app.run(debug=True)
