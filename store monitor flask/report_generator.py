import pandas as pd
import pytz
from datetime import datetime, timedelta
import sqlite3  # Import SQLite3 module
from database import execute_query  # Assuming this function exists in `database.py`
import os  # For directory and file path handling

def generate_report():
    try:
        # Step 1: Get the maximum timestamp from the store_status table
        current_timestamp = execute_query("SELECT MAX(timestamp_utc) FROM store_status")[0][0]
        current_timestamp = pd.to_datetime(current_timestamp)

        # Step 2: Fetch all data from the database
        connection = sqlite3.connect("store_monitoring.db")  # Connect to SQLite database
        store_status_df = pd.read_sql_query("SELECT * FROM store_status", connection)
        business_hours_df = pd.read_sql_query("SELECT * FROM business_hours", connection)
        timezones_df = pd.read_sql_query("SELECT * FROM timezones", connection)
        connection.close()  # Close the database connection

        # Step 3: Default timezone
        default_timezone = pytz.timezone("America/Chicago")

        # Step 4: Merge timezone information into store_status_df
        store_status_df = store_status_df.merge(timezones_df, on="store_id", how="left")
        store_status_df["timezone_str"] = store_status_df["timezone_str"].fillna("America/Chicago")
        store_status_df["timezone"] = store_status_df["timezone_str"].apply(pytz.timezone)

        # Step 5: Convert UTC timestamps to local time
        store_status_df["timestamp_utc"] = pd.to_datetime(store_status_df["timestamp_utc"])  # Ensure UTC timestamps are parsed
        store_status_df["timestamp_local"] = store_status_df.apply(
            lambda row: handle_timestamp(row["timestamp_utc"], row["timezone"]), axis=1
        )

        # Step 6: Calculate uptime/downtime for each store
        report_data = []
        for store_id in store_status_df["store_id"].unique():
            store_data = store_status_df[store_status_df["store_id"] == store_id]
            business_hours = business_hours_df[business_hours_df["store_id"] == store_id]

            # Default to 24/7 if no business hours are provided
            if business_hours.empty:
                business_hours = pd.DataFrame({
                    "day_of_week": range(7),
                    "start_time_local": ["00:00:00"] * 7,
                    "end_time_local": ["23:59:59"] * 7
                })

            # Process uptime/downtime for different time ranges
            uptime_last_hour, downtime_last_hour = calculate_uptime_downtime(store_data, current_timestamp, hours=1)
            uptime_last_day, downtime_last_day = calculate_uptime_downtime(store_data, current_timestamp, days=1)
            uptime_last_week, downtime_last_week = calculate_uptime_downtime(store_data, current_timestamp, days=7)

            # Append results to the report data
            report_data.append([
                store_id,
                uptime_last_hour, uptime_last_day, uptime_last_week,
                downtime_last_hour, downtime_last_day, downtime_last_week
            ])

        # Step 7: Save the report to a CSV file in the specified directory
        reports_dir = r"D:\store monitor flask\reports"  # Define the directory path
        os.makedirs(reports_dir, exist_ok=True)  # Create the directory if it doesn't exist
        report_path = os.path.join(reports_dir, "report.csv")  # Full path to the report file

        report_df = pd.DataFrame(report_data, columns=[
            "store_id", "uptime_last_hour", "uptime_last_day", "uptime_last_week",
            "downtime_last_hour", "downtime_last_day", "downtime_last_week"
        ])
        report_df.to_csv(report_path, index=False)  # Save the report to the specified path
        print(f"Report saved successfully at: {report_path}")  # Confirm file creation

    except Exception as e:
        print(f"An error occurred while generating the report: {e}")

def handle_timestamp(timestamp_utc, timezone):
    """
    Handle naive and tz-aware timestamps and convert them to the desired timezone.
    """
    if timestamp_utc.tzinfo is None:  # Check if the timestamp is naive
        return timestamp_utc.tz_localize("UTC").tz_convert(timezone)
    else:  # If the timestamp is already timezone-aware
        return timestamp_utc.tz_convert(timezone)

def calculate_uptime_downtime(store_data, current_timestamp, hours=None, days=None):
    """
    Calculate uptime and downtime for a given store within a specified time range.
    """
    try:
        # Determine the time range start based on hours or days
        if hours:
            time_range_start = current_timestamp - timedelta(hours=hours)
        elif days:
            time_range_start = current_timestamp - timedelta(days=days)

        # Filter data within the specified time range
        filtered_data = store_data[
            (store_data["timestamp_local"] >= time_range_start) &
            (store_data["timestamp_local"] <= current_timestamp)
        ]

        # Calculate uptime and downtime
        uptime = filtered_data[filtered_data["status"] == "active"]["status"].count() * 60  # Convert to minutes
        downtime = filtered_data[filtered_data["status"] == "inactive"]["status"].count() * 60  # Convert to minutes

        return uptime, downtime

    except Exception as e:
        print(f"An error occurred while calculating uptime/downtime: {e}")
        return 0, 0
