import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from database.connect import engine
import json
from sqlalchemy import inspect


def fetch_data(station_id_to_fetch, pest_id_to_fetch='1'):
    metadata = MetaData()
    station_stats_table = Table('station_stats', metadata, autoload_with=engine)
    pests_table = Table('pests', metadata, autoload_with=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    results_station_stats = session.query(station_stats_table).filter(station_stats_table.c.stationID == station_id_to_fetch).all()
    results_pests = session.query(pests_table).filter(pests_table.c.id == pest_id_to_fetch).all()

    results_station_stats_dict = [station._asdict() for station in results_station_stats]
    results_pests_dict = [pest._asdict() for pest in results_pests]

    calculate_pest_gens(results_station_stats_dict, results_pests_dict)

    json_results = json.dumps(results_station_stats_dict, default=str)  # default=str to handle non-serializable data types
    session.close()

    return json_results


def calculate_pest_gens(results_station_stats_dict, results_pests_dict):
    df_station = pd.DataFrame.from_dict(results_station_stats_dict)
    df_pest = pd.DataFrame(results_pests_dict)

    print(df_station)
    print(df_pest)
