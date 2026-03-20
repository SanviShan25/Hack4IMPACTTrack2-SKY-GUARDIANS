# ==========================================
# SKY GUARDIAN BACKEND (FINAL FIXED)
# ==========================================

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# 🔥 VERY IMPORTANT FIX
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


data_store = []

# ------------------------------
# UPDATE ROUTE
# ------------------------------
@app.route('/update', methods=['POST'])
def update():
    data = request.json
    data_store.append(data)

    response = jsonify({"message": "OK"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200

# ------------------------------
# DATA ROUTE
# ------------------------------
@app.route('/data', methods=['GET'])
def get_data():
    response = jsonify(data_store)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200


# ------------------------------
# SUPPLY ROUTE (FIXED)
# ------------------------------
@app.route('/request_supply', methods=['POST'])
def supply():
    data = request.json
    print("📦 Supply Request:", data)
    return jsonify({"message": "Supply received"}), 200


# ------------------------------
# RUN
# ------------------------------
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)