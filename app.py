from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# MongoDB 연결
client = MongoClient("mongodb+srv://bchdaeuo:bchdaeuo@cluster0.053hdai.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["EduProject"]
ranking_collection = db["Rankings"]

# 닉네임이 null일 때 대체하는 정리 함수
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

# 랭킹 제출
@app.route("/submit", methods=["POST"])
def submit_ranking():
    try:
        data = request.get_json()
        logging.info(f"[수신된 데이터] {data}")

        # 중복 데이터 체크 조건
        duplicate_check = {
            "uid": data.get("uid"),
            "game_mode": data.get("game_mode"),
            "grade_score": data.get("grade_score"),
            "level": data.get("level"),
            "grade": data.get("grade"),
            "elapsed_time": data.get("elapsed_time"),
            "correct_rate": data.get("correct_rate"),
        }

        # 중복 여부 확인
        existing = ranking_collection.find_one(duplicate_check)

        if existing:
            logging.warning("[중복 제출] 동일한 랭킹이 이미 존재합니다")
            return jsonify({
                "status": "duplicate",
                "message": "이미 랭킹에 등록되었습니다"
            }), 409

        # 새로운 데이터 저장
        ranking_collection.insert_one(data)
        return jsonify({"status": "success", "message": "Ranking submitted successfully"}), 200

    except Exception as e:
        logging.error(f"[제출 오류] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 랭킹 조회
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
                    "uid": 1,
                    "nickname": 1,
                    "game_mode": 1,
                    "grade_score": 1,
                    "level": 1,
                    "grade": 1,
                    "elapsed_time": 1,
                    "correct_rate": 1
                }
            ).sort("grade_score", -1).limit(100)
        )

        cleaned = [clean_record(r) for r in records]
        return jsonify({"status": "success", "ranking": cleaned}), 200

    except Exception as e:
        logging.error(f"[랭킹 조회 오류] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 기본 루트
@app.route("/")
def home():
    return "랭킹 서버가 원활히 작동하고 있습니다."

# 서버 상태 확인
@app.route("/status", methods=["GET"])
def status():
    server_status = {
        "server": "online",
        "message": "로그인 및 회원가입 서버가 정상 작동 중입니다."
    }

    try:
        client.admin.command("ping")
        server_status["database"] = "online"
    except Exception as e:
        server_status["database"] = "offline"
        server_status["db_error"] = str(e)

    return jsonify(server_status)

# 서버 사용량 확인
@app.route("/metrics")
def metrics():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    net = psutil.net_io_counters()

    return jsonify({
        "cpu_percent": cpu,
        "memory_percent": mem.percent,
        "sent_MB": round(net.bytes_sent / 1024 / 1024, 2),
        "recv_MB": round(net.bytes_recv / 1024 / 1024, 2)
    })

# 서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
