import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from database.connect import engine
import json
from sqlalchemy import inspect
import os
import matplotlib.pyplot as plt
import numpy as np


def fetch_data(station_id_to_fetch, pest_id_to_fetch='1'):
    metadata = MetaData()
    station_stats_table = Table('station_stats', metadata, autoload_with=engine)
    pests_table = Table('pests', metadata, autoload_with=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    results_station_stats = session.query(station_stats_table).filter(
        station_stats_table.c.stationID == station_id_to_fetch).all()
    results_pests = session.query(pests_table).filter(pests_table.c.id == pest_id_to_fetch).all()

    results_station_stats_dict = [station._asdict() for station in results_station_stats]
    results_pests_dict = [pest._asdict() for pest in results_pests]

    calculate_pest_gens(results_station_stats_dict, results_pests_dict)

    json_results = json.dumps(results_station_stats_dict,
                              default=str)  # default=str to handle non-serializable data types
    session.close()

    return json_results


def calculate_pest_gens(results_station_stats_dict, results_pests_dict):
    df_station = pd.DataFrame.from_dict(results_station_stats_dict)
    df_pest = pd.DataFrame(results_pests_dict)

    pest_base_temp = df_pest['baseTemperature'].iloc[0]
    pest_max_temp = df_pest['maxTemperature'].iloc[0]
    pest_total_temp = df_pest['totalTemperature'].iloc[0]
    pest_ideal_hum = df_pest['idealHumidity'].iloc[0]

    df_station.set_index("measurementDate", inplace=True)

    full_index = pd.date_range(start=df_station.index.min(), end=df_station.index.max(), freq="D")
    df_station = df_station.reindex(full_index)

    # Interpolate missing values linearly
    df_station = df_station.interpolate(method="linear")

    day_degrees = []
    for day_min, day_max in zip(df_station['minAirT'].values, df_station['maxAirT'].values):
        t_min = max(day_min, pest_base_temp)
        t_max = min(day_max, pest_max_temp)
        day_degree = max(0, ((t_min + t_max) / 2) - pest_base_temp)
        day_degrees.append(day_degree)
    df_station['day_degree'] = day_degrees

    gens = []
    cumulative = 0
    for day_degree in df_station['day_degree'].values:
        cumulative = cumulative + day_degree
        gen = cumulative / pest_total_temp
        gens.append(gen)
    df_station['gen'] = gens

    adj_day_degrees = []
    for day_hum, day_degree in zip(df_station['meanAirH'].values, df_station['day_degree'].values):
        alpha = np.exp(-(((day_hum - pest_ideal_hum) / 30) ** 2))
        adj_day_degree = day_degree * alpha
        adj_day_degrees.append(adj_day_degree)
    df_station['adj_day_degree'] = adj_day_degrees

    adj_gens = []
    cumulative = 0
    for adj_day_degree in df_station['adj_day_degree'].values:
        cumulative = cumulative + adj_day_degree
        adj_gen = cumulative / pest_total_temp
        adj_gens.append(adj_gen)
    df_station['adj_gen'] = adj_gens

    # Plotting the 'day_degree' column against the index (or another column, like 'date')
    plt.figure(figsize=(10, 6))
    plt.plot(df_station.index, df_station['gen'], label='Generations', color='b')
    plt.plot(df_station.index, df_station['adj_gen'], label='Adjusted Generations', color='r')

    # Adding labels and title
    plt.xlabel('Date')  # or you can use 'Index' if the index represents dates
    plt.ylabel('Generations')
    plt.title('Generations over time')
    plt.legend()

    file_path = 'generations_plot.png'  # Modify the filename or provide a full path if needed
    plt.savefig(file_path, dpi=300, bbox_inches='tight')

    # Confirm if the file is saved
    if os.path.exists(file_path):
        print(f"Plot saved successfully as {file_path}")
    else:
        print("Failed to save the plot.")


fetch_data('107052024')
