from flask import Flask, jsonify, request
import threading
import uuid
from report_generator import generate_report

app = Flask(__name__)

# In-memory storage for report status
reports = {}

@app.route("/trigger_report", methods=["POST"])
def trigger_report():
    report_id = str(uuid.uuid4())
    reports[report_id] = {"status": "Running"}

    # Start report generation in a background thread
    threading.Thread(target=run_report_generation, args=(report_id,)).start()

    return jsonify({"report_id": report_id})

@app.route("/get_report", methods=["GET"])
def get_report():
    report_id = request.args.get("report_id")
    if report_id not in reports:
        return jsonify({"error": "Invalid report_id"}), 404

    report_status = reports[report_id]["status"]
    if report_status == "Complete":
        return jsonify({"status": "Complete", "file": "report.csv"})
    else:
        return jsonify({"status": "Running"})

def run_report_generation(report_id):
    generate_report()
    reports[report_id]["status"] = "Complete"

if __name__ == "__main__":
    from database import initialize_db
    initialize_db()  # Initialize database and load data
    app.run(debug=True)