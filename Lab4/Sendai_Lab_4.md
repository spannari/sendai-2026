# Lab 4: The Video Edge Gateway

Transform your Raspberry Pi into a simulated CCTV Hub that manages virtual cameras, mobile phone feeds, and real-time data overlays. We use MediaMTX, a lightweight media server that converts RTSP/RTMP streams into browser-friendly formats like HLS.

## Part 1: Prep work

1. Create the working directory. We'll use the same folder in all of the following excerices.

   ```bash
   mkdir my-video-gateway && cd my-video-gateway
   ```

2. Copy the two video files and put them in the folder. Or you can choose your own versions.
   [Camera feed 1](./img/camera_feed.mp4)
   [Camera feed 2](./img/camera_feed2.mp4) 1. Download the files in a folder on your laptop. 2. Open a **new terminal window** (not logged into SSH), and run the following command:
   `bash
        scp camera_feed.mp4 [username]@[pi-ip]:~/my-video-gateway/
        ` 3. Repeat for the other file.

## Part 2: Single camera

1. **Create `docker-compose.yml`** in the same directory:

```yaml
services:
  mediamtx:
    image: bluenviron/mediamtx:latest
    container_name: video-server
    ports:
      - "8554:8554" # RTSP
      - "8888:8888" # HLS (Web View)
    restart: always

  camera-1:
    image: mwader/static-ffmpeg:latest
    container_name: camera-1
    depends_on:
      - mediamtx
    volumes:
      - .:/live
    command: -re -stream_loop -1 -i /live/camera_feed.mp4 -c copy -f rtsp rtsp://mediamtx:8554/cam1
```

1. **Run:** `docker compose up -d`
2. **Test:** Visit `http://[PI-IP]:8888/cam1` in your laptop browser.

## Part 3: Two camera setup

**The Challenge:** Can you modify your code to add a second camera?

- **Goal:** You want a service that streams second file (`camera_feed2.mp4`) to the path another path.
- **Watch out:** Ensure your indentation (the spaces on the left) stays perfectly aligned!

<details>
 <summary>Test yourself first, solution here.</summary>
If you got stuck, update your `docker-compose.yml` to this version.

```yaml
services:
  mediamtx:
    image: bluenviron/mediamtx:latest
    container_name: video-server
    ports:
      - "8554:8554" # RTSP
      - "8888:8888" # HLS (Web View)
    restart: always

  camera-1:
    image: mwader/static-ffmpeg:latest
    container_name: camera-1
    depends_on:
      - mediamtx
    volumes:
      - .:/live
    command: -re -stream_loop -1 -i /live/camera_feed.mp4 -c copy -f rtsp rtsp://mediamtx:8554/cam1

  camera-2:
    image: mwader/static-ffmpeg:latest
    container_name: camera-2
    depends_on:
      - mediamtx
    volumes:
      - .:/live
    command: -re -stream_loop -1 -i /live/camera_feed2.mp4 -c copy -f rtsp rtsp://mediamtx:8554/cam2
```

</details>

- **Test:** Open two tabs: `http://[PI-IP]:8888/cam1` and `http://[PI-IP]:8888/cam2`.

## Part 4: Streaming from Larix to your own media server

Connect your physical hardware to the digital gateway.

1. Find out the IP address of your Raspberry Pi. HOW?
2. Open **Larix Broadcaster** on your phone.
3. Create a new connection as in Lab 3.
4. **URL:** `rtsp://[PI-IP]:8554/phone`
5. **Start Stream** on your phone.
6. **View it:** Go to `http://[PI-IP]:8888/phone` on your laptop browser.
   > _Scenario: This simulates a technician sending a live feed of a machine back to the control room._

## Part 5: Resource testing

Let's see what happens when the Pi has to "process" video instead of just moving it.

1. Run `docker stats` and watch the CPU % for `camera-1`. (It should be very low).
2. Edit the `command` for `camera-1` to this "Heavy" version that adds a **Live Timestamp**:

```yaml
command: >
  -re -stream_loop -1 -i /live/camera_feed.mp4
  -vf "drawtext=text='%{localtime}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:x=10:y=10"
  -c:v libx264 -preset ultrafast -tune zerolatency -f rtsp rtsp://mediamtx:8554/cam1
```

- What does the command do:
  - `-i /live/camera_feed.mp4` **Source Ingestion:** Defines the input media source for the processing pipeline.
  - `-vf "drawtext=..."` **Video Filtering:** Applies a metadata overlay. The drawtext filter modifies the raw pixel data to include a dynamic system time string.
  - `-c:v libx264` **Video Encoder:** Specifies the H.264 software codec. This forces the system to re-calculate every frame to integrate the filter modifications.
  - `-preset ultrafast` **Encoding Optimization:** Instructs the encoder to prioritize processing speed over compression efficiency, reducing the CPU load on Edge hardware.
  - `-tune zerolatency` **Latency Reduction:** Minimizes internal frame buffering to ensure the output stream remains synchronized with the real-time source.
  - `-f rtsp` **Container Muxing:** Encapsulates the processed video stream into the Real-Time Streaming Protocol for network transmission.

1. Run `docker compose up -d` and check `docker stats` again.

- **The Lesson:** Notice the CPU spike. This happens because the video is being re-encoded in real time, which is computationally expensive compared to simply copying the stream. If you want to observe how this effects Pi, run command `vcgencmd measure_temp`

## Part 6: Some more FFmpeg tinkering

FFmpeg is a command-line tool used to record, convert (transcode), and process media. In our setup, FFmpeg handles the video processing before sending the stream to MediaMTX.

1. Modify the "Heavy" command from Part 5 so the timestamp appears at the bottom-right of the screen instead of the top-left.

        - Hint: Use `W-tw-10` and `H-th-10` for your coordinates
        - Remember to update the correct .yml-file and always `docker compose down && docker compose up -d`

    <details>

```yaml
command: >
  -re -stream_loop -1 -i /live/camera_feed.mp4
  -vf "drawtext=text='%{localtime}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:x=W-tw-10:y=H-th-10"
  -c:v libx264 -preset ultrafast -tune zerolatency -f rtsp rtsp://mediamtx:8554/cam1
```

</details>

1. In industrial IoT, we often need to "brand" a feed or add a watermark. Let's test this with the tools we have. Copy the supplied [Overlay logo](./img/m_logo.png) (or create your own) and copy it to Pi like in Part 1. Update the command for `camera-1` to merge the video and the logo. Check the result, and remember to check the CPU load.

<details>

```yaml
command: >
  -re -stream_loop -1 -i /live/camera_feed.mp4 -i /live/m_logo.png
  -filter_complex "[0:v][1:v]overlay=x=W-w-10:y=10"
  -c:v libx264 -preset ultrafast -f rtsp rtsp://mediamtx:8554/cam1
```

</details>

## Discussion

1. The Scalability Question: "We saw Camera 1 hit 70% CPU for one stream. If we had 10 cameras that all needed timestamps, would this Raspberry Pi survive? Or 100?"
2. The Professional Way: High-end IP cameras use dedicated hardware (OSD chips) or Client-Side Rendering (the browser draws the logo). Why is this better?
3. The Bandwidth vs. Power Trade-off: "Why did we use -c copy for Camera 2? What is the benefit?"
4. The Industrial Reality: "If you were a technician, would you rather watch 100 video feeds, or have an API send you a text message only when a camera goes offline?"

## Key Take-aways

- **Media pipelines:** Video flows through ingestion (RTSP) → processing → output (HLS)
- **Edge processing cost:** Real-time video transformation increases CPU usage significantly
- **Containerized media systems:** Media servers like MediaMTX can scale video routing without hardware changes

## Things to try if you want more challenges

1. **Unwanted areas:** In industrial sites, we sometimes need to blur or cover sensitive areas. Use the `drawbox` filter in the ffmpeg command to place a black square over a portion of camera-1.
2. **Expert challenge:** In Part 5, we observed that burning a timestamp into the video pixels (Transcoding) is computationally expensive, consuming significant CPU resources. In professional IoT architecture, we often use Client-Side Rendering to keep the Edge Gateway load near 0%.
   Revert camera-1 to the lightweight -c copy mode (reducing CPU to <2%), yet still display a live, ticking clock over the video feed in a web browser.
   **Pointers for research** - Instead of changing the video data, think about how web developers use CSS Positioning (position: absolute and z-index) to stack a transparent text element directly on top of a video player. - Use JavaScript (setInterval) to update the time in your overlay every 1000ms. - You cannot easily edit the internal MediaMTX pages. Instead, try creating a simple index.html file on your laptop that embeds the HLS stream URL in an `<iframe>` or a dedicated player like `hls.js`.
