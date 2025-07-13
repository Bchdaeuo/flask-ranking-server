from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS 문제 예방

@app.route('/submit', methods=['POST'])
def submit_rank():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    print("[서버] 랭킹 데이터 수신:", data)
    # 여기서 MongoDB 저장 로직 넣으면 됩니다.

    return jsonify({'status': 'success', 'message': 'Ranking submitted successfully'})

@app.route('/')
def index():
    return "Edu Project Ranking Server"

if __name__ == '__main__':
    app.run(debug=True)