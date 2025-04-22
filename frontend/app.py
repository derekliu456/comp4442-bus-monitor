from flask import Flask, jsonify, send_from_directory
import json, os

app = Flask(__name__, static_folder="static")

@app.route("/stream")
def stream():
    path = os.path.join("data","agg","kpi.json")
    return jsonify(json.load(open(path)))

@app.route("/summary")
def summary():
    data = json.load(open("data/agg/kpi.json"))
    return jsonify({
      "routes":[d["route"] for d in data],
      "punctual":[d["punctual"] for d in data],
      "delay5":[d["delay5"] for d in data]
    })

@app.route("/")
def index():
    return send_from_directory("static","index.html")

if __name__=="__main__":
    app.run(debug=True)
