from flask import Flask, render_template, jsonify
from pymongo import MongoClient
import subprocess
from urllib.parse import quote_plus

app = Flask(__name__)

# URL encode your MongoDB username and password
username = quote_plus("shreyashk289")
password = quote_plus("Shreyas@2003")

# MongoDB configuration
MONGO_URI = f"mongodb+srv://{username}:{password}@twitter.rc0mj.mongodb.net/?retryWrites=true&w=majority&appName=Twitter"
DATABASE_NAME = "twitter_trends"
COLLECTION_NAME = "trending_topics"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run-script", methods=["POST"])
def run_script():
    try:
        # Run the Python script that fetches Twitter trends
        result = subprocess.run(
            ["python3", "Twitter.py"],
            check=False,  # Don't raise exception for errors, we'll check manually
            capture_output=True,  # Capture stdout and stderr
            text=True  # Decode output as text
        )

        # Check if there is any error in stderr
        if result.stderr:
            return jsonify({"status": "error", "message": f"Script failed with error: {result.stderr}"})

        # Check the return code (non-zero indicates failure)
        if result.returncode != 0:
            return jsonify({"status": "error", "message": f"Script failed with exit code {result.returncode}"})

        # If the script completed successfully (no error in stderr, and returncode 0)
        return jsonify({"status": "success", "message": "Script executed successfully!"})

    except Exception as e:
        # Catch any unexpected errors
        return jsonify({"status": "error", "message": f"An unexpected error occurred: {str(e)}"})


@app.route("/get-trends", methods=["GET"])
@app.route("/get-trends", methods=["GET"])
def get_trends():
    try:
        # Fetch all trends from MongoDB sorted by timestamp (latest first)
        trends_data = list(
            collection.find({}, {"_id": 0})  # Exclude MongoDB ObjectId
            .sort("timestamp", -1)  # Sort by timestamp in descending order
        )
        return jsonify({"status": "success", "data": trends_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":
    app.run(debug=False)
