import logging
from database.models import StationStats
from sqlalchemy.orm import Session
from database.connect import engine
from station_fetcher.fetcher import fetch_data_from_influxdb
from database.models import Base
import math
from station_fetcher import station_ids
from sqlalchemy import and_
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.exc import SQLAlchemyError
from datetime import timezone, timedelta

# Configure logging
logging.basicConfig(
    filename="station_data_processing.log",  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

# Initialize database session
session = Session(bind=engine)
Base.metadata.create_all(bind=engine)


def process_station_data(station_ids, fetch_all):
    logging.info(f"Starting data processing for station_ids={station_ids}, fetch_all={fetch_all}")
    all_station_data = []

    # Fetch and clean data for each station_id
    for station_id in station_ids:
        try:
            start_time = time.time()  # Start timer for the station

            # Fetch data
            data = fetch_data_from_influxdb(station_id, fetch_all=fetch_all)

            # Replace 'nan' with None in the dataset
            cleaned_data = [
                {key: None if isinstance(value, float) and math.isnan(value) else value for key, value in
                 record.items()}
                for record in data
            ]

            # Append the cleaned data to the common list
            all_station_data.extend(cleaned_data)
            end_time = time.time()  # End timer for the station

            # Log the execution time for the station
            logging.info(f"Fetched and cleaned data for station_id={station_id} in {end_time - start_time:.2f} seconds")

        except Exception as e:
            logging.error(f"Error fetching data for station_id={station_id}: {e}")

    # Perform database operations
    try:
        # Start the timer for the database operations
        operation_start_time = time.time()

        for item in all_station_data:
            # Check if a record with the same stationID and measurementDate exists
            existing_record = session.query(StationStats).filter(
                and_(
                    StationStats.stationID == item["stationID"],
                    StationStats.measurementDate == item["measurementDate"]
                )
            ).first()

            if existing_record:
                # Update the existing record
                for key, value in item.items():
                    if key != "id":  # Avoid updating the primary key
                        setattr(existing_record, key, value)
            else:
                # Insert a new record
                new_record = StationStats(**item)
                session.add(new_record)

        # Commit changes after all operations
        session.commit()

        # End the timer for the database operations
        operation_end_time = time.time()
        logging.info(f"Database operation execution time: {operation_end_time - operation_start_time:.2f} seconds.")

    except SQLAlchemyError as e:
        session.rollback()  # Rollback in case of error
        logging.error(f"An error occurred during database operations: {e}")
    finally:
        # Always close the session
        session.close()


if __name__ == "__main__":
    process_station_data(station_ids, fetch_all=False)
