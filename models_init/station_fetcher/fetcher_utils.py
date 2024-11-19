from datetime import datetime, timedelta
import pandas as pd


def generate_flux_queries(bucket, measurement, host, station_id, fetch_all=False):
    last_filter = ""
    TASHKENT_OFFSET_NANOSECONDS = 5 * 60 * 60 * 1_000_000_000  # 5 hours
    if fetch_all:
        range_clause = f'''
            start: -inf,
            stop: time(v: int(v: now()) + {TASHKENT_OFFSET_NANOSECONDS} - int(v: duration(v: 1d)))
        '''
    else:
        range_clause = f'''
            start: time(v: int(v: now()) + {TASHKENT_OFFSET_NANOSECONDS} - int(v: duration(v: 2d))),
            stop: time(v: int(v: now()) + {TASHKENT_OFFSET_NANOSECONDS} - int(v: duration(v: 1d)))
        '''

        last_filter = "|> last()"

    def generate_flux_query(field, agg_fn, agg_label):
        return f"""
                {field}_{agg_label} = from(bucket: "{bucket}")
                  |> range({range_clause})
                  |> filter(fn: (r) => r["_measurement"] == "{measurement}")
                  |> filter(fn: (r) => r["_field"] == "{field}")
                  |> filter(fn: (r) => r["host"] == "{host}")
                  |> filter(fn: (r) => r["stationID"] == "{station_id}")
                  |> aggregateWindow(every: 1d, fn: {agg_fn}, createEmpty: false, timeSrc: "_start")
                  |> set(key: "aggregation", value: "{agg_label}")
                  {last_filter}
                """

    # Define fields and their aggregations
    fields = [
        ("AirH", "mean"), ("AirH", "min"), ("AirH", "max"),
        ("AirT", "mean"), ("AirT", "min"), ("AirT", "max"),
        ("Rain", "sum"),
        ("WindS", "mean"), ("WindS", "min"), ("WindS", "max"),
        ("SoilT", "mean"), ("SoilT", "min"), ("SoilT", "max"),
        ("SoilEC", "mean"), ("SoilEC", "min"), ("SoilEC", "max"),
        ("SoilVWC", "mean"), ("SoilVWC", "min"), ("SoilVWC", "max"),
    ]

    # Generate individual queries
    query_strings = []
    for field, agg in fields:
        query_strings.append(generate_flux_query(field, agg, agg))

    # Generate the union query
    union_query = "union(tables: [\n" + ",\n".join([f"  {field}_{agg}" for field, agg in fields]) + "\n])"

    # Combine everything into a single string
    complete_query = "\n".join(query_strings) + "\n" + union_query

    return complete_query


def get_previous_day_timestamps(today):
    start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate the start and stop for the previous day
    start_of_previous_day = start_of_today - timedelta(days=1)
    stop_of_previous_day = start_of_today - timedelta(seconds=1)

    # Convert to ISO 8601 format strings (this is what Flux expects)
    start_str = start_of_previous_day.isoformat() + "Z"
    stop_str = stop_of_previous_day.isoformat() + "Z"

    return start_str, stop_str


def convert_into_dictionary(result, station_id, fetch_all):
    # Create an empty list to store the records
    records_list = []

    # Iterate over the tables in the result
    for table in result:
        # Iterate over the records in each table
        for record in table.records:
            # Extract necessary fields and create a dictionary
            record_data = {
                "measurementDate": record["_time"],
                "field": record["_field"],
                "value": record["_value"],
                "aggregation": record["aggregation"],
                "stationID": record["stationID"],
            }

            # Add the dictionary to the list of records
            records_list.append(record_data)

    if not fetch_all and len(records_list) == 0:
        return []

    df = pd.DataFrame(records_list)

    # print(df.stationID)

    df['field'] = df['aggregation'] + df['field']
    df.drop(['aggregation'], axis=1, inplace=True)

    # Convert 'time' column to datetime if it isn't already
    df.index = pd.to_datetime(df.index)

    pivot_df = df.pivot(index='measurementDate', columns='field', values='value')

    pivot_df.columns.name = None
    pivot_df['stationID'] = df['stationID'].iloc[0]
    pivot_df = pivot_df.reset_index()

    # Convert each row in the DataFrame to a dictionary with column names as keys
    return pivot_df.to_dict(orient='records')
