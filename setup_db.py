"""
Configuración inicial de la base de datos.
Ejecutar UNA VEZ después de clonar el repositorio (o para resetear el esquema).

    python setup_db.py

Pasos que realiza:
  1. Elimina la base de datos existente (si la hay) para evitar conflictos de esquema
  2. Crea la base de datos con el DDL v2.0
  3. Carga los datos de prueba desde data/datos_parqueadero.xlsx

Requisitos previos:
  - Tener MariaDB/MySQL corriendo
  - Haber creado el archivo .env a partir de .env.example con tus credenciales
  - pip install -r requirements.txt
"""
import sys
import os
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import dotenv
dotenv.load_dotenv(dotenv.find_dotenv())

try:
    import mariadb
except ImportError:
    print("ERROR: mariadb no está instalado. Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

HOST = os.getenv("DB_HOST", "localhost")
USER = os.getenv("DB_USER", "root")
PASS = os.getenv("DB_PASSWORD", "")
DB   = "gestion_parqueadero"

EXCEL = pathlib.Path(__file__).parent / "data" / "datos_parqueadero.xlsx"


def main():
    if not EXCEL.exists():
        print(f"ERROR: No se encontró {EXCEL}")
        print("El archivo de datos debe estar en data/datos_parqueadero.xlsx")
        sys.exit(1)

    print("=== Setup GestionParqueadero ===\n")

    # 1. Conectar sin base de datos y eliminar la existente
    try:
        conn = mariadb.connect(host=HOST, user=USER, password=PASS)
    except mariadb.OperationalError as e:
        print(f"ERROR: No se pudo conectar a MariaDB: {e}")
        print("Verifica tus credenciales en el archivo .env")
        sys.exit(1)

    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS `{DB}`")
    conn.commit()
    cur.close()
    conn.close()
    print(f"OK Base de datos '{DB}' eliminada (o no existia)")

    # 2. Crear esquema nuevo via bootstrap
    from config.db import _bootstrap
    _bootstrap()
    print("OK Esquema v2.0 creado correctamente")

    # 3. Cargar datos desde Excel
    print()
    from database.dml_loader import run as load_data
    load_data()

    print("\n=== Setup completado ===")
    print(f"Ejecuta 'python main.py' para iniciar la aplicacion.")
    print(f"Login: cedula={os.getenv('ADMIN_CEDULA','1000000000')}  contrasena={os.getenv('ADMIN_PASS','admin123')}")


if __name__ == "__main__":
    main()
