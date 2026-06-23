# run_sql_file.py
import os
import psycopg2

  
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_FILE = os.path.join(BASE_DIR, "init_schema.sql")


def run_sql_file():
    # Connect to Postgres
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Read and execute SQL file
    with open(SQL_FILE, "r") as f:
        sql_commands = f.read()

    try:
        cur.execute(sql_commands)
        print("SQL script executed successfully!")
    except Exception as e:
        print("Error executing SQL script:", e)

    cur.close()
    conn.close()

if __name__ == "__main__":
    run_sql_file()
