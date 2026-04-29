# Lab 2: Raspberry Pi simulating edge device

In this lab, we turn the Raspberry Pi into an **Edge Device**. We'll build an API that simulates an industrial sensor. We will learn how simple apps can lose data and how **Docker Volumes** make an Edge device reliable enough for production use.

## Part 1: Connect and Prep the Raspberry Pi

Before we can command the Pi, we have to remote log in from laptop.

- **Command:** `ssh [username]@[pi-ip-address]`
- Username and password are given to you by the teacher
- **Goal:** You should see the command prompt change to something like `pi@raspberrypi:~ $`.

- **Install Docker:** (Skip if already installed)

  ```bash
  curl -sSL https://get.docker.com | sh
  sudo usermod -aG docker $USER
  ```

  _Note: If you just installed Docker, log out (`exit`) and log back in._

## Part 2: The Volatile Sensor (RAM Only)

_If the container stops, the data is lost. This is volatile memory._

### A. Create the Setup

Create a new folder called `my-edge-sensor`. Put all the files following in next steps into this directory.

```bash
mkdir my-edge-sensor
cd my-edge-sensor
```

### B. Create the `Dockerfile`

Create a file named `Dockerfile` (no extension) in the folder `my-edge-sensor`. You can use any editor you like, this example uses nano.

```bash
nano Dockerfile
```

Write or copy this to your file:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
RUN pip install flask
COPY sensor_app.py .
CMD ["python", "sensor_app.py"]
```

This will install Python and Flask for creating the sensor.

### C. Create the simple logic with Python (`sensor_app.py`)

```python
from flask import Flask, jsonify
import random

app = Flask(__name__)
latest_reading = {"temperature": 0.0, "status": "waiting"}

# the function for generating random values for temperature and setting status
@app.route('/update')
def update():
    global latest_reading
    latest_reading = {"temperature": round(random.uniform(20, 30), 2), "status": "active"}
    return "Local RAM updated!"

# shows the data in JSON
@app.route('/sensor')
def get_sensor():
    return jsonify(latest_reading)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### D. Launch with Compose

Create `docker-compose.yml`:

```yaml
services:
  sensor-api:
    build: .
    container_name: sensor-service
    ports:
      - "5000:5000" # Use 5001 if on a Mac!
```

**Run:** `docker compose up -d --build`
_Note: The `--build` flag is required whenever you change the Dockerfile or the initial script!_

### E. The Failure Test

1. Open `http://[PI-IP]:5000/update`, then `/sensor`. Note the reading. # again, use 5001 on a Mac.
2. **Wipe the container:** `docker compose down`. (This deletes the current containers. It happens because containers are ephemeral: when removed, their internal filesystem is deleted unless data is stored outside the container.)
3. **Restart:** `docker compose up -d`.
4. Check `/sensor`. **The data reset to 0.0** This is why IoT-devices need persistence of some form.

Notice how /update gives you a confirmation message, but /sensor gives you raw JSON. Why? Because a human reads the update, but a app reads the sensor data. There are ways to make JSON more readable for humans, which we'll use in the next part.

## Part 3: The Industrial-like Sensor (Disk Persistence)

_Usage of Atomic Writes and Docker Volumes to make data survive power down._

### A. Upgrade to the Professional Script (`sensor_app.py`)

Replace your script with this version. It adds **Thread Safety**, **Atomic File Replacement**, and a **"Sensor Data"**-section for you to add more sensors easily.

```python
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
```

### B. Building the bridge between Pi and Container (`docker-compose.yml`)

Update your file to include the **Volume**. This links the Pi's physical SD card to the container's internal `/app` folder.

```yaml
services:
  sensor-api:
    build: .
    container_name: sensor-service
    volumes:
      - .:/app # Bridge: Host folder <-> Container folder
    ports:
      - "5000:5000" # Use 5001 if on a Mac!
    restart: always
```

### C. The Persistence test

1. Run `docker compose up -d --build`.
2. Hit `/update`.
3. **Wipe the container** Run `docker compose down`.
4. **Restart** Run `docker compose up -d`.
5. Check `/sensor`. The data should've survived.

## Troubleshooting & Tips

- **Manual Overwrite:** Want to force a specific value? Use the terminal:
  `curl -X POST -H "Content-Type: application/json" -d '{"temperature": 99.9, "status": "FIRE"}' http://localhost:5000/update` If you are using Windows, you might need to "escape" the quotes.
- **Network Binding:** The `host='0.0.0.0'` in Python is vital. It tells the Pi to listen to the whole Wi-Fi network, not just itself.
- **Cache Issues:** If the numbers don't change on refresh, try a "Hard Refresh" (**Ctrl+Shift+R** or **Cmd+Shift+R**). This was taken care of in the latter .py-script, but just a heads-up, if it deos not work.
  **Inside container:** Use `docker exec -it sensor-service cat sensor_storage.json` to see the data from _inside_ the container.

## Key Take-aways

- **RAM vs. Disk:** You now know that containers are temporary, but data should be permanent. This uses a solution for local computer. The much more common way is to send data to cloud.
- **Atomic Writes:** Using a `.tmp` file ensures the Pi doesn't corrupt your data if the power is cut.
- **Docker Volumes:** This is the bridge that allows a virtual container to save files on physical hardware. Volumes do not empty, unless spesifically told to do so.
- **HTTP vs. MQTT:** We used an API (HTTP) here because it is a "Pull" system. It is perfect for an app, asking for a specific piece of data. MQTT is a "Push" system—better for sensors constantly streaming data to a broker. Since we aren't coordinating a whole fleet of sensors yet, a direct API is faster and simpler to build.

## Things to try if you want more challenges

1. **Multi-Value Challenge:** Go to the "Sensor data" in the code and add a "humidity" key with a random value between 20 and 80.
2. **Safety Alarm:** Add logic to the update_sensor function so that if the temperature is over 30.0, the status automatically changes from "active" to "ALARM".
3. **Remote Override:** Use the curl command in your laptop terminal to remotely change the sensor_id of your Pi. Can you make it show your own name in the JSON?
4. **Timestamping**: Import datetime and add a "timestamp" key so we know exactly when the sensor was read.
5. **Over-achiever:** If you have the skills, and too much time on your hands, you can build a dashboard for the JSON. Or have the data to be saved to database. But you are on your own in this!
