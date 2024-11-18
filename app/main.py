from flask import Flask, request, jsonify
from test import persist_station_data

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, Docker with Gunicorn and Reloading'


@app.route('/stationID/<string:id>', methods=['GET'])
def fetch_station_data(id):
    # Step 1: Get the stationID from the request body
    station_id_to_fetch = id

    if not station_id_to_fetch:
        return jsonify({"error": "stationID is required"}), 400

    return jsonify(persist_station_data(station_id_to_fetch))


if __name__ == '__main__':
    app.run(debug=True)
