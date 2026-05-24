import mariadb
import os
import pathlib
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

_HOST = os.getenv('DB_HOST', 'localhost')
_USER = os.getenv('DB_USER', 'root')
_PASS = os.getenv('DB_PASSWORD', '')
_DB   = 'gestion_parqueadero'

DB_CONFIG = {
    'host': _HOST,
    'user': _USER,
    'password': _PASS,
    'database': _DB,
}

_DDL_PATH = pathlib.Path(__file__).parent.parent / 'database' / 'ddl.sql'


def _bootstrap():
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
        # Strip comment lines so leading comments don't cause the whole chunk to be skipped
        lines = [l for l in stmt.split('\n') if not l.strip().startswith('--')]
        clean = '\n'.join(lines).strip()
        if not clean:
            continue
        upper = clean.upper()
        if upper.startswith('CREATE DATABASE') or upper.startswith('USE '):
            continue
        try:
            cur.execute(clean)
        except mariadb.ProgrammingError:
            pass
    conn.commit()

    # Bootstrapear admin inicial desde .env si no existe
    admin_cedula = os.getenv('ADMIN_CEDULA', '1000000000')
    admin_nombre = os.getenv('ADMIN_NOMBRE', 'Admin')
    admin_apellido = os.getenv('ADMIN_APELLIDO', 'Sistema')
    admin_correo = os.getenv('ADMIN_CORREO', 'admin@parqueadero.com')
    admin_pass = os.getenv('ADMIN_PASS', 'admin123')
    admin_codigo = os.getenv('ADMIN_CODIGO', 'ADM-001')

    cur.execute("SELECT cedula FROM Administrador WHERE cedula = %s", (admin_cedula,))
    if not cur.fetchone():
        cur.execute(
            "SELECT cedula FROM Usuario WHERE cedula = %s", (admin_cedula,)
        )
        if not cur.fetchone():
            cur.execute(
                """INSERT INTO Usuario (cedula, primer_nombre, primer_apellido, correo)
                   VALUES (%s, %s, %s, %s)""",
                (admin_cedula, admin_nombre, admin_apellido, admin_correo)
            )
        from datetime import date
        cur.execute(
            """INSERT INTO Administrador (cedula, contrasenia, fecha_asignacion, codigo_interno)
               VALUES (%s, %s, %s, %s)""",
            (admin_cedula, admin_pass, date.today().isoformat(), admin_codigo)
        )
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
