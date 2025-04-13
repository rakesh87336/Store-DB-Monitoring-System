import sqlite3
import pandas as pd
from pathlib import Path

# Initialize SQLite database and load CSV data into tables
def initialize_db(db_path="store_monitoring.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_status (
            store_id TEXT,
            timestamp_utc TEXT,
            status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_hours (
            store_id TEXT,
            day_of_week INTEGER,
            start_time_local TEXT,
            end_time_local TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timezones (
            store_id TEXT,
            timezone_str TEXT
        )
    """)
    conn.commit()

    # Load data from CSV files into tables
    
    store_status_df = pd.read_csv(r"D:\store monitor flask\data\store_status.csv")
    business_hours_df = pd.read_csv(r"D:\store monitor flask\data\store_status.csv")
    timezones_df = pd.read_csv(r"D:\store monitor flask\data\timezones.csv")

    store_status_df.to_sql("store_status", conn, if_exists="replace", index=False)
    business_hours_df.to_sql("business_hours", conn, if_exists="replace", index=False)
    timezones_df.to_sql("timezones", conn, if_exists="replace", index=False)

    conn.close()

# Utility function to execute queries
def execute_query(query, params=()):
    conn = sqlite3.connect("store_monitoring.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result
