from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# ✅ 여기에 URI 삽입
client = MongoClient("mongodb+srv://bchdaeuo:5Bf9gbd589!@cluster0.053hdai.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# 원하는 DB와 컬렉션 선택
db = client["EduProject"]
ranking_collection = db["Rankings"]

@app.route("/submit", methods=["POST"])
def submit_ranking():
    try:
        data = request.get_json()
        print("[수신된 데이터]", data)
        ranking_collection.insert_one(data)
        return jsonify({"status": "success", "message": "Ranking submitted successfully"}), 200
    except Exception as e:
        print("[오류]", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/")
def home():
    return "Edu Project Ranking Server"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
