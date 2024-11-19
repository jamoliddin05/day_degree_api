from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from database.connect import engine
import json
from sqlalchemy import inspect


def persist_station_data(station_id_to_fetch):
    metadata = MetaData()
    station_stats_table = Table('station_stats', metadata, autoload_with=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(station_stats_table).filter(station_stats_table.c.stationID == station_id_to_fetch).all()

    results_dict = [station._asdict() for station in results]

    json_results = json.dumps(results_dict, default=str)  # default=str to handle non-serializable data types
    session.close()

    return results_dict
