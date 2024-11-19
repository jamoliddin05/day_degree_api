from .fetcher_utils import generate_flux_queries, convert_into_dictionary
import time
from . import *


def fetch_data_from_influxdb(station_id, fetch_all=False):
    # Get the environment variables
    token = os.getenv("INFLUXDB_TOKEN")
    org = os.getenv("INFLUXDB_ORG")
    bucket = os.getenv("INFLUXDB_BUCKET")
    url = os.getenv("INFLUXDB_URL")
    host = os.getenv("INFLUXDB_HOST")
    measurement = os.getenv("INFLUXDB_MEASUREMENT")

    # Initialize the InfluxDB client
    client = InfluxDBClient(url=url, token=token, org=org, timeout=30000)

    # Generate the Flux query
    query = generate_flux_queries(
        bucket=bucket,
        measurement=measurement,
        host=host,
        station_id=station_id,
        fetch_all=fetch_all
    )

    print(query)

    start_time = time.time()
    # Query InfluxDB and get the result
    result = client.query_api().query(org=org, query=query)

    # Convert the result into a dictionary
    response = convert_into_dictionary(result, station_id, fetch_all)
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Execution time for {station_id}: {elapsed_time:.2f} seconds")
    return response
