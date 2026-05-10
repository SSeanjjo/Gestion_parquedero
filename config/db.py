import mariadb
import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('USER', 'root'),
    'password': os.getenv('PASSWORD', ''),
    'database': 'gestion_parqueadero',
}


def get_connection():
    conn = mariadb.connect(**DB_CONFIG)
    conn.autocommit = False
    return conn
