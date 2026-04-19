# Reference Guide: Linux and Docker for IoT

This document provides the essential command reference and workflow tips for the laboratory exercises. It covers basic navigation, container management, and troubleshooting procedures.

## Part 1: Basic Linux and Remote Access
These commands are used to access and navigate the Raspberry Pi file system.

* **ssh [username]@[pi-ip-address]**
    - Secure Shell: Connects your laptop to the Raspberry Pi's terminal remotely.
* **scp [file] [user]@[ip]:~/folder/**
    - Secure Copy: Transfers files (such as video files or scripts) from your laptop to the Raspberry Pi.
* **ls**
    - Lists all files and folders in the current directory.
* **cd [directory_name]**
    - Change Directory: Moves you into the specified folder. Use `cd ..` to move up one level.
* **mkdir [directory_name]**
    - Creates a new folder.
* **rm [file_name]**
    - Removes a file. Use `rm -r [folder_name]` to remove a directory and its contents.
* **nano [file_name]**
    - Opens a text editor to create or modify files. 
    - Save: `Ctrl + O`, then `Enter`. Exit: `Ctrl + X`.

---

## Part 2: Docker and Compose Commands
Standard operations for managing containerized IoT services.

* **docker ps**
    - Lists all currently running containers. Use `docker ps -a` to see stopped containers.
* **docker logs [container_name]**
    - Displays the output logs of a container. Essential for debugging Python code errors.
* **docker stats**
    - Displays a live stream of container resource usage, specifically CPU and Memory.
* **docker compose up -d**
    - Starts all services defined in the `docker-compose.yml` file in detached mode.
* **docker compose up -d --build**
    - Rebuilds the images before starting containers. Required after modifying a `Dockerfile` or `sensor_app.py` in a lab.
* **docker compose down**
    - Stops and removes all containers, networks, and images defined in the Compose file.
* **docker system prune -a**
    - **WARNING:** This command deletes ALL unused containers, networks, and images on the system. Use this only to free up disk space; it will remove any downloaded images that are not currently running in an active container.

---

## Part 3: MQTT and Network Tools
Used for testing communication between brokers and clients.

* **mosquitto_sub -h [host] -t [topic]**
    - Subscribes to a topic to listen for messages.
* **mosquitto_pub -h [host] -t [topic] -m "[message]"**
    - Publishes a message to a specific topic.
* **hostname -I**
    - Displays the IP address of the Raspberry Pi.
* **vcgencmd measure_temp**
    - Returns the current CPU temperature of the hardware. Essential for Lab 4.

---

## Part 4: Workflow Tips for Success

* **Tabbed Terminals:** Keep one terminal window open for "Listening" (e.g., `mosquitto_sub`) and a second window for "Acting" (e.g., `mosquitto_pub` or `docker compose`).
* **The "Hard Refresh":** If sensor data or video streams seem stuck in the browser, use **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac) to bypass the browser cache.
* **Case Sensitivity:** Remember that MQTT topics (`sendai/test`) and Stream URLs (`rtsp://.../cam1`) are case-sensitive. `Cam1` and `cam1` are different paths.
* **YAML Indentation:** Docker Compose files rely on spaces. Never use the "Tab" key; use exactly two spaces for each level of indentation.
* **JSON Syntax:** Ensure all keys and string values are enclosed in **double quotes** (`" "`). Single quotes will cause the Python backend to fail.

---

## Part 5: Troubleshooting and Connectivity

### Common Errors
1. **Port Conflicts:** `Bind for 0.0.0.0:[PORT] failed`.
   - *Solution:* Run `docker stop $(docker ps -q)` to clear old containers using those ports.
2. **Permissions:** `permission denied`.
   - *Solution:* Ensure the user is in the `docker` group or prefix the command with `sudo`.
3. **JSON Decode Error:** - *Solution:* Validate your JSON message for missing quotes, trailing commas, or mismatched brackets.

### Connectivity Checklist
If a service is unreachable:
1. Verify both the laptop and the Raspberry Pi are on the same Wi-Fi network.
2. Ensure the Python application is bound to host `0.0.0.0` (all interfaces) rather than `127.0.0.1`.
3. Use `ping [PI-IP-ADDRESS]` from your laptop terminal to verify the hardware is reachable.
4. If you are on a Mac, use port **5001** for Flask instead of **5000** to avoid OS conflicts.