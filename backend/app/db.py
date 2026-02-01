import os
from psycopg import connect

DB_URL = os.environ["DATABASE_URL"]

def get_conn():
    return connect(DB_URL)
