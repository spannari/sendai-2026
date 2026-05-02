from flask import Flask, jsonify, request
import json, random, os, threading

# Thread safety
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
DATA_FILE = "sensor_storage.json"
lock = threading.Lock()

# ---------- File handling ----------
def save_to_disk(data):
    try:
        with lock:
            temp_file = DATA_FILE + ".tmp"
            with open(temp_file, "w") as f:
                json.dump(data, f)
            os.replace(temp_file, DATA_FILE) # Atomic write prevents file corruption
    except Exception as e:
        print(f"Error saving data: {e}")

def load_from_disk():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
    return {"sensor_id": "PI-SENDAI-01", "temperature": 0.0, "status": "no_data_yet"}

# ---------- Sensor Data ----------
@app.route('/update', methods=['GET', 'POST'])
def update_sensor():
    # 1. Default Simulated Data (Add new sensors here!)
    new_data = {
        "sensor_id": "PI-SENDAI-01",
        "temperature": round(random.uniform(20, 32), 2),
        "status": "active"
    }

    # 2. Support Manual Overwrites (For testing or App control)
    req_data = request.get_json(silent=True)
    if req_data:
        new_data.update(req_data) # Merges user data into our dictionary

    save_to_disk(new_data)
    # This forces the JSON to indent by 4 spaces in the browser to make it more readable. You can remove the indent argument if you prefer compact JSON.
    return json.dumps({"message": "Data saved to SD Card", "data": new_data}, indent=4), 200, {'Content-Type': 'application/json'}

    # Compact version without indentation
    # return jsonify({"message": "Data saved to SD Card", "data": new_data})
# ---------- End of Sensor Data ----------

@app.route('/sensor')
def get_data():
    return jsonify(load_from_disk())

# no cache, with old browser support
@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
