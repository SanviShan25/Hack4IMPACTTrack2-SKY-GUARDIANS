from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# 🔥 IMPORT ML STREAM
from ML import generate_frames

app = Flask(__name__)
CORS(app)

data_store = []

# ------------------------------
# RECEIVE ML DATA
# ------------------------------
@app.route('/update', methods=['POST'])
def update():
    data = request.json
    data_store.append(data)
    return jsonify({"message": "OK"}), 200

# ------------------------------
# SEND DATA TO FRONTEND
# ------------------------------
@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data_store), 200

# ------------------------------
# SUPPLY REQUEST
# ------------------------------
@app.route('/request_supply', methods=['POST'])
def supply():
    data = request.json
    print("📦 Supply Request:", data)
    return jsonify({"message": "Supply received"}), 200

# ------------------------------
# 🔥 LIVE VIDEO STREAM ROUTE
# ------------------------------
@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# ------------------------------
# RUN SERVER
# ------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
