from flask import Flask, jsonify, request
import socket
import datetime

# Initialize Flask app
app = Flask(__name__)

# Root route
@app.route('/', methods=['GET'])
def home():
    return "Welcome to Sandeep's app ......"

# Health check route
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "host": socket.gethostname()
    })

# Echo route
@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json() or {}
    return jsonify({"echo": data})

# Run the app
if __name__ == "__main__":
    # Bind to all interfaces so it’s reachable via 127 and 192 IPs
    app.run(host="0.0.0.0", port=5000, debug=True)
