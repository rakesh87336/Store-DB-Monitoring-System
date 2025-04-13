# Store Monitoring System

The Store Monitoring System is a robust Flask-based web application designed to monitor store uptime and downtime. It generates detailed reports based on store status data, business hours, and timezones, providing insights into store activity over different time ranges (last hour, last day, last week).

This project adheres to best practices in software development, including well-structured code, handling edge cases, optimized performance, and clear documentation of logic.

Table of Contents
Features
Project Structure
Optimizations and Best Practices
Prerequisites
Setup Instructions
Usage
API Endpoints
Logic for Uptime/Downtime Calculation
Contributing
License
Features
Trigger + Poll Architecture: Supports asynchronous report generation with a trigger (POST) and poll (GET) mechanism.
Database Integration: Efficiently reads data from SQLite tables (store_status, business_hours, timezones) to compute metrics.
Timezone Handling: Converts UTC timestamps to local time using store-specific timezones.
Default Business Hours: Automatically assigns 24/7 business hours if none are provided.
CSV Output: Generates a structured report.csv file with uptime and downtime metrics for each store.
Corner Case Handling: Handles missing data, invalid timestamps, and overlapping business hours gracefully.
Performance Optimization: Optimized for large datasets with efficient filtering and aggregation logic.
Project Structure



![image](https://github.com/user-attachments/assets/70b8dbcf-a088-4f23-bf13-fe7cbfe3d79e)


Optimizations and Best Practices
1. Well-Structured Code
The project is modular, with clear separation of concerns:
app.py: Handles API endpoints and threading.
database.py: Manages database initialization and queries.
report_generator.py: Contains the core logic for report generation.
Functions are small, focused, and reusable, adhering to the Single Responsibility Principle.
2. Handling Corner Cases
Missing or incomplete data in the database is handled gracefully:
Default timezone (America/Chicago) is assigned if none is provided.
Default business hours (24/7) are used for stores without defined hours.
Invalid or malformed timestamps are skipped during processing.
3. Optimized Performance
Efficient Filtering: Data is filtered only within the relevant time range to minimize memory usage.
Vectorized Operations: Pandas is used extensively for vectorized operations, ensuring fast computation.
Background Processing: Report generation runs in a background thread to prevent blocking the main application.
4. Clear Documentation
Inline comments and docstrings explain the purpose and logic of each function.
Key algorithms (e.g., uptime/downtime calculation) are documented in detail below.
Prerequisites
Before running the application, ensure you have the following installed:

Python 3.8 or higher
SQLite3
Required Python libraries:
Flask
pandas
pytz
sqlite3
You can install the required libraries using:



pip install flask pandas pytz
Setup Instructions
Clone the Repository:

git clone https://github.com/your-username/store-monitoring.git
cd store-monitoring

Install Dependencies:

pip install -r requirements.txt

Prepare Data Files:
Place your input CSV files (store_status.csv, business_hours.csv, timezones.csv) in the data/ directory.

Ensure the files follow the expected format:
store_status.csv: store_id, timestamp_utc, status
business_hours.csv: store_id, day_of_week, start_time_local, end_time_local
timezones.csv: store_id, timezone_str

Initialize the Database:
Run the following command to create the SQLite database and load data:

python database.py

Run the Application:

   Start the Flask server:

python app.py

Usage

Trigger Report Generation
Send a POST request to trigger report generation:


curl -X POST http://127.0.0.1:5000/trigger_report
Response:

{
  "report_id": "unique-report-id"
}

Check Report Status

Use the GET endpoint to check the status of the report:


curl "http://127.0.0.1:5000/get_report?report_id=unique-report-id"
Possible Responses:

If the report is still being generated:

{
  "status": "Running"
}

If the report is complete:

{
  "status": "Complete",
  "file": "report.csv"
}

Download the Report
Once the report is complete, find the report.csv file in the reports/ directory.

API Endpoints
/trigger_report
POST
Triggers report generation and returns a
report_id
.
/get_report
GET
Checks the status of the report using
report_id
.

Logic for Uptime/Downtime Calculation
The uptime and downtime calculations are performed as follows:

1. Filter Data by Time Range
For each store, filter the store_status data to include only records within the specified time range (last hour, last day, last week).

3. Handle Business Hours
If business hours are provided, compute the overlap between the store's active hours and the time range.
If no business hours are provided, assume the store operates 24/7.

5. Calculate Uptime and Downtime
Count the number of active and inactive statuses within the filtered data.
Convert the counts to minutes (1 status = 1 minute).

Example:

uptime = filtered_data[filtered_data["status"] == "active"]["status"].count() * 60
downtime = filtered_data[filtered_data["status"] == "inactive"]["status"].count() * 60

4. Edge Case Handling
If there is no data for a store within the time range, uptime and downtime are set to 0.
Overlapping business hours are handled by merging intervals before calculating uptime/downtime.

Acknowledgments
Built using Flask for the web framework.
Data processing powered by Pandas .
Timezone handling provided by pytz .
