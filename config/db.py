import mariadb
import os
import pathlib
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

_HOST = os.getenv('DB_HOST', 'localhost')
_USER = os.getenv('USER', 'root')
_PASS = os.getenv('PASSWORD', '')
_DB   = 'gestion_parqueadero'

DB_CONFIG = {
    'host': _HOST,
    'user': _USER,
    'password': _PASS,
    'database': _DB,
}

_DDL_PATH = pathlib.Path(__file__).parent.parent / 'database' / 'ddl.sql'


def _bootstrap():
    """Crea la base de datos y las tablas si no existen."""
    conn = mariadb.connect(host=_HOST, user=_USER, password=_PASS)
    cur = conn.cursor()
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS `{_DB}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    conn.commit()
    cur.close()
    conn.close()

    conn = mariadb.connect(host=_HOST, user=_USER, password=_PASS, database=_DB)
    cur = conn.cursor()
    with open(_DDL_PATH, encoding='utf-8') as f:
        raw = f.read()
    for stmt in raw.split(';'):
        stmt = stmt.strip()
        if not stmt:
            continue
        upper = stmt.upper()
        if upper.startswith('--') or upper.startswith('CREATE DATABASE') or upper.startswith('USE '):
            continue
        try:
            cur.execute(stmt)
        except mariadb.ProgrammingError:
            pass
    conn.commit()
    cur.close()
    conn.close()


def get_connection():
    try:
        conn = mariadb.connect(**DB_CONFIG)
        conn.autocommit = False
        return conn
    except mariadb.OperationalError as e:
        if 'Unknown database' in str(e):
            _bootstrap()
            conn = mariadb.connect(**DB_CONFIG)
            conn.autocommit = False
            return conn
        raise
