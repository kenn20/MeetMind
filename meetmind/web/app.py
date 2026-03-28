import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".env"))

from flask import Flask, request, jsonify, render_template
from flow import flow

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/process", methods=["POST"])
def process():
    audio_file = request.files.get("file")
    if not audio_file:
        return jsonify({"error": "No file uploaded"}), 400

    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, audio_file.filename)
    audio_file.save(file_path)

    result = flow.invoke(
        file_path=file_path,
        meeting_title=request.form.get("title", "Team Meeting"),
        engineer_name=request.form.get("engineer", "Engineer"),
        designer_name=request.form.get("designer", "Designer"),
        pm_name=request.form.get("pm", "PM"),
        project_name=request.form.get("project", ""),
    )

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
