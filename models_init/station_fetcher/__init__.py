import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load environment variables
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_HOST = os.getenv("INFLUXDB_HOST")
INFLUXDB_MEASUREMENT = os.getenv("INFLUXDB_MEASUREMENT")

# Initialize a client instance
client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG,
    timeout=30000
)


def fetch_station_ids(client):
    # Define the query
    query = '''
        from(bucket: "oxus2")
      |> range(start: -10d)
      |> filter(fn: (r) => r["_measurement"] == "meteometric")
      |> keep(columns: ["stationID"])
      |> distinct(column: "stationID")
      |> yield(name: "stationIDs")
    '''

    # Run the query
    result = client.query_api().query(org=INFLUXDB_ORG, query=query)

    # Process the result into a list of stationID values
    station_ids = []
    for table in result:
        for record in table.records:
            station_ids.append(str(record["stationID"]))  # Ensure stationID is a string

    # Close the client
    client.close()

    return station_ids


station_ids = fetch_station_ids(client)
