from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from urllib.parse import quote_plus

import os

db_password = os.getenv("DB_PASSWORD")

if not db_password:
    raise RuntimeError("DB_PASSWORD is not set")

db_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER", "postgres") ,
    password=db_password,
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    database=os.getenv("DB_NAME", "devpulse_tracker") ,
)

Engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind = Engine )