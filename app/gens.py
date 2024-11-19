from database.connect import *
import pandas as pd
from itertools import accumulate
import numpy as np

stations_table_name = 'station_stats'  # Replace with your actual table name
pests_table_name = 'pests'
models_table_name = 'models'


def fetch_and_convert_df(table_name, id, condition):
    table = Table(table_name, metadata, autoload_with=engine)
    stmt = select(table).where(condition(table, id))
    results = session.execute(stmt).fetchall()
    df = pd.DataFrame([result._asdict() for result in results])

    return df


def station_condition(table, id):
    return table.c.stationID == id


def pest_condition(table, id):
    return table.c.id == id


def model_condition(table, id):
    return table.c.id == id


def calculate_day_degrees(station_id, pest_id):
    station_df = fetch_and_convert_df(stations_table_name, station_id, station_condition)
    pest_df = fetch_and_convert_df(pests_table_name, pest_id, pest_condition)

    pest_base_temp = pest_df['baseTemperature'].iloc[0]
    pest_max_temp = pest_df['maxTemperature'].iloc[0]
    pest_total_temp = pest_df['totalTemperature'].iloc[0]
    pest_ideal_hum = pest_df['idealHumidity'].iloc[0]

    day_degrees = []
    for day_min, day_max in zip(station_df['minAirT'].values, station_df['maxAirT'].values):
        temp_min = max(day_min, pest_base_temp)
        temp_max = min(day_max, pest_max_temp)
        day_degree = max(0, ((temp_min + temp_max) / 2) - pest_base_temp)
        day_degrees.append(round(day_degree, 2))

    cum_dds = list(accumulate(day_degrees))
    cum_dds = [round(value, 2) for value in cum_dds]

    gens = []
    for cum_dd in cum_dds:
        gen = cum_dd / pest_total_temp
        gens.append(gen)
    gens = [round(value, 2) for value in gens]

    adj_day_degrees = []
    for day_hum, day_degree in zip(station_df['meanAirH'].values, day_degrees):
        alpha = np.exp(-(((day_hum - pest_ideal_hum) / 30) ** 2))
        adj_day_degree = day_degree * alpha
        adj_day_degrees.append(round(adj_day_degree, 2))

    cum_adj_dds = list(accumulate(adj_day_degrees))
    cum_adj_dds = [round(value, 2) for value in cum_adj_dds]

    adj_gens = []
    for cum_adj_day_degree in cum_adj_dds:
        adj_gen = cum_adj_day_degree / pest_total_temp
        adj_gens.append(adj_gen)

    adj_gens = [round(value, 2) for value in adj_gens]

    return day_degrees, cum_dd, gens, adj_gens
