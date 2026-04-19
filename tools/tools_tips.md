# Lab Tools and Tips

This document outlines the hardware and software environment required for our lab sessions. Success in these labs depends on a reliable connection between Raspberry Pi, Phone and your development environment (Laptop).

## Tools

### Hardware

1.  **Laptop:** Your primary development station for writing code and managing containers.
2.  **Mobile Phone:** Used as a video source.
3.  **Raspberry Pi:** Our "Edge Gateway".
4.  **Wi-Fi Mobile Router:** Provides the local area network (LAN) that allows all devices to communicate.

### Software

1.  **Code Editor:** [VS Code](https://code.visualstudio.com/) is the industry standard for development. You can use the one you want.
2.  **Containerization:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) must be installed and running on your laptop. You'll do this in lab 1.
3.  **Mobile Streaming:** [Larix Broadcaster](https://softvelum.com/larix/)
4.  **Media Testing:** [VLC Media Player](https://www.videolan.org/vlc/) is used to verify video streams.
5.  **Git:** Optional. If you haven't used it yet, maybe do not start right now. Or if you do, read the first chapters of the [book](https://git-scm.com/book/en/v2) carefully.

-----

## Tips & Manuals

### Essential Reading and Manuals

  * **[Docker CLI Cheat Sheet (PDF)](https://docs.docker.com/get-started/docker_cheatsheet.pdf):** A quick reference for container management.
  * **[The Linux Command Line (Reference)](https://linuxcommand.org/lc3_learning_the_shell.php):** A thorough guide for those new to the Shell/Terminal environment and bash commands.
  * **[FFmpeg Documentation](https://ffmpeg.org/ffmpeg.html):** The manual for video transcoding and stream manipulation used in Lab 4.
  * **[MediaMTX Guide](https://github.com/bluenviron/mediamtx):** You can find out more about the media server from the documentation. This is for reference, not really needed in basic labs.

### Pro Tips for the Lab

  * **Terminal Management:** IoT development often requires seeing two things at once. Use "Split Screen" or multiple tabs in your terminal—one to watch incoming data (Subscriber) and one to send commands (Publisher).
  * **Network Isolation:** If you cannot connect to your Pi, ensure your laptop hasn't accidentally switched back to the school's general Wi-Fi. All devices must stay on the mobile router's network.
  * **The "Clean Slate" Method:** If your Docker environment becomes cluttered or ports are blocked, use `docker stop $(docker ps -q)` to stop all active processes before starting the next exercise.
  * **Case Sensitivity:** In Linux and MQTT, `Sensor1` and `sensor1` are completely different entities. Always use lowercase for filenames and topics to avoid confusion.
  * **Verify, Don't Guess:** Before assuming your code is broken, use `ping [IP-ADDRESS]` from your laptop terminal to verify the hardware is still online.

-----