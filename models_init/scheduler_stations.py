from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from main import process_station_data
from station_fetcher import station_ids
from datetime import timezone, timedelta
import logging
import time

# Set up the scheduler
scheduler = BackgroundScheduler()

scheduler.add_job(
    process_station_data,
    trigger=CronTrigger(
        hour=0, minute=10, timezone=timezone.utc
    ),
    args=[station_ids, False],  # Arguments for the function
    id="process_station_data_job",  # Optional ID for the job
    replace_existing=True  # Replace if job with the same ID exists
)

# Start the scheduler
scheduler.start()
logging.info("Scheduler has started. Tasks will run every day at 5:10 am by Tashkent timezone.")

# Keep the script running
try:
    while True:
        time.sleep(1)  # Keeps the script alive
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    logging.info("Scheduler stopped.")
