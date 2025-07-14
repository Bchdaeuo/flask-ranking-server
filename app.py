from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# ✅ MongoDB 연결
client = MongoClient("mongodb+srv://bchdaeuo:bchdaeuo@cluster0.053hdai.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["EduProject"]
ranking_collection = db["Rankings"]

# ✅ 닉네임이 null일 때 대체하는 정리 함수
def clean_record(record):
    return {
        "nickname": record.get("nickname", "익명") if record.get("nickname") != "null" else "익명",
        "game_mode": record.get("game_mode", "알 수 없음"),
        "grade_score": record.get("grade_score", 0),
        "level": record.get("level", 1),
        "grade": record.get("grade", "F"),
        "elapsed_time": record.get("elapsed_time", "00:00"),
        "correct_rate": record.get("correct_rate", 0)
    }

# ✅ 랭킹 제출
@app.route("/submit", methods=["POST"])
def submit_ranking():
    try:
        data = request.get_json()
        logging.info(f"[수신된 데이터] {data}")
        ranking_collection.insert_one(data)
        return jsonify({"status": "success", "message": "Ranking submitted successfully"}), 200
    except Exception as e:
        logging.error(f"[제출 오류] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ✅ 랭킹 조회
@app.route("/get_ranking", methods=["GET"])
def get_ranking():
    try:
        mode = request.args.get("mode", "all")
        base_query = {"grade_score": {"$gte": 0}}

        if mode == "classic":
            base_query["game_mode"] = "클래식"
        elif mode == "speed":
            base_query["game_mode"] = "스피드"
        # else: mode == "all" → 필터 없음

        records = list(
            ranking_collection.find(
                base_query,
                {
                    "_id": 0,
                    "nickname": 1,
                    "game_mode": 1,
                    "grade_score": 1,
                    "level": 1,
                    "grade": 1,
                    "elapsed_time": 1,
                    "correct_rate": 1
                }
            ).sort("grade_score", -1).limit(10)
        )

        cleaned = [clean_record(r) for r in records]
        return jsonify({"status": "success", "ranking": cleaned}), 200

    except Exception as e:
        logging.error(f"[랭킹 조회 오류] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ✅ 기본 루트
@app.route("/")
def home():
    return "Edu Project Ranking Server is running"

# ✅ 서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
