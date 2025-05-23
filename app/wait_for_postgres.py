# wait_for_postgres.py
import time
import psycopg2
import sys

for i in range(30):
    try:
        conn = psycopg2.connect(
            dbname="testdb",
            user="postgres",
            password="Paddi_1984",
            host="db",
            port="5432"
        )
        print("Database is ready!")
        conn.close()
        sys.exit(0)
    except psycopg2.OperationalError:
        print("Waiting for database to be ready...")
        time.sleep(2)

print("Database not ready after 30 tries.")
sys.exit(1)
