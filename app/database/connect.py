from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker
from . import *

# Define the connection URL for root user with no password
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Create a session
Session = sessionmaker(bind=engine)
session = Session()
