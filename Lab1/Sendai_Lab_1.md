# Lab 1: Docker, MQTT and JSON

## Part 1: Docker tutorial on your laptop

- View and do the [Getting Started tutorial](https://docs.docker.com/get-started/introduction/)
  - If `docker compose watch` command fails, try `docker compose up --watch` instead
  - Example app can be cloned from [GitHub](https://github.com/docker/getting-started-todo-app)
  - for just learning the basics, you can do modules 1 + 2. If you want to learn more about when it gets powerful, do also module 3.

- Tip: type `docker` to see all available commands.
- Tip: [Docker Cheat Sheet PDF for CLI](https://docs.docker.com/get-started/docker_cheatsheet.pdf)

## Part 2: Testing MQTT with Docker on your laptop

Now that you know how to run a container using Docker, we are going to use a spesific service called **Message Broker** running inside a container.

In IoT, sensors don't usually talk directly to other devices. They send a message to a broker, and the devices pick them up from there. We will use **Mosquitto**, which is a popular open-source IoT broker.

### 1. Pull the Mosquitto Image

First, we need to download the Mosquitto container from the internet.
Open your terminal and run:

```bash
docker pull eclipse-mosquitto
```

### 2. Start the broker

We will run the broker in **detached** mode (in the background). We need to open port **1883**, which is the standard port for MQTT messages.

**Run this command:**

```bash
docker run -d --name my-broker -p 1883:1883 eclipse-mosquitto
```

> **Check it:** Run `docker ps`. Do you see `my-broker` running?

### 3. The Listener (Subscriber)

To see messages, we need to listen to a specific channel, called a **topic** (-t). Open a **NEW Terminal window** (keep the other one open) and run this command to start listening:

```bash
docker run --rm -it --network host eclipse-mosquitto mosquitto_sub -h localhost -t "sendai/test"
```

_Note: This window will look like it's frozen. It is actually waiting for a message._

- --rm
  - Automatically removes the container when it stops
  - Keeps your system clean (no leftover containers)
- -it
  - -i → interactive (keeps STDIN open)
  - -t → allocates a terminal
  - Together: lets you see live output and interact if needed

### 4. The Sender (Publisher)

Go back to your **First Terminal window**. We are going to broadcast a **message** (-m) to the channel we just opened, to a spesific topic.

**Run this command:**

```bash
docker run --rm -it --network host eclipse-mosquitto mosquitto_pub -h localhost -t "sendai/test" -m 'Hello Sendai!'
```

**Look at your Second Terminal window.** You should see `Hello Sendai!` appear instantly.

## Part 3: Moving on from simple commands to Dockerfile and .yaml

Typing long commands is slow, plus you have to remember them. What follows is one example of how setups can be automated. In real projects, Docker Compose is often used alone, and Dockerfiles are used when custom images or build steps are needed. We'll introduce Docker volumes in the next lab, which provide an alternative way to handle configuration in this setup, making the Dockerfile optional in this specific case.

### 1. Create the Setup

Create a new folder called `my-broker-setup`. Inside that folder, create these **three** files:

**File 1: `mosquitto.conf`**
_(This tells the broker to listen for messages and allow connections without a password)._

```text
listener 1883
allow_anonymous true
```

**File 2: `Dockerfile`**
_(This builds your custom broker image and includes your config file)._

```dockerfile
FROM eclipse-mosquitto:latest
COPY mosquitto.conf /mosquitto/config/mosquitto.conf
EXPOSE 1883
```

**File 3: `docker-compose.yml`**
_(This manages the container launch)._

```yaml
services:
  broker:
    build: .
    container_name: my-broker
    ports:
      - "1883:1883"
    restart: always
```

### 2. Launch with One Command

First, stop any old manual brokers:
`docker stop my-broker && docker rm my-broker`

Now, launch your new automated version from inside your folder:

```bash
docker compose up -d
```

These files automate the broker setup from steps 1 & 2. If you want to test this, you can run steps 3 & 4 again. In a simple setup like this, using files will not speed up the process that much. But when you have multiple services, networks, and configurations, Docker Compose becomes much faster and easier to manage.

Remember the simple MQTT setup: 'Publisher → Broker → Subscriber'

### 3. Extra task: Publishing to cloud

You can test the capabilities of MQTT protocol with public broker. Use the **HiveMQ Public Broker** to simulate a real world use case, where you would send sensor data to cloud.

1. **Publish to the Cloud:**

   ```bash
   docker run --rm eclipse-mosquitto mosquitto_pub -h broker.hivemq.com -t "sendai/test/YOURNAME" -m 'Greetings from Sendai!'
   ```

   Use a unique topic so you don’t mix messages with others.
2. **See it Live:** Go to [HiveMQ Web Client](https://www.hivemq.com/demos/websocket-client/), click **Connect**, and subscribe to the topic `sendai/test/YOURNAME`. This works because MQTT brokers can be accessed over the internet, not just locally

**Important**: If everybody used `sendai/test` as a topic, you would see everyone's messages mixed together. Using unique topics (like `sendai/test/YOURNAME`) helps avoid this confusion. But try a wildcard here `#` for subscription. What do you see?

However, this does not provide **security**. On a public broker, anyone can subscribe to `#` or `sendai/test/#` and see all messages. Therefore, do not send any confidential information (e.g., usernames or passwords) nor should you use public broker for real data. In real case we would use authentication, authorization and/or isolation to make the system secure.

## Part 4: Intro to JSON

For next lab we'll have a preview of how JSON is used. Before we send a message, we need to know how to write it. IoT devices can use **JSON** (JavaScript Object Notation). It is a simple way to organize data using "keys" and "values."

**Simple JSON syntax:**

1. Everything is wrapped in curly braces: `{ }`
2. Data comes in pairs: `"Key": "Value"`
3. Keys and Strings must have **Double Quotes** (`" "`).
4. Numbers do **NOT** need quotes.
5. Pairs are separated by commas (`,` ).

**Example for publishing city weather in JSON:**
`{"city": "Sendai", "outside_temperature": 20}`

You can now test on sending your message as in previous excercises. See, if you can get the message to show up in the listener.

## Final Challenge for the Lab

**Build your own command** to send sensor data from a factory.

### Your Goal

1. Open a listener on a new topic: `sensor/data`
2. In a second terminal, use `mosquitto_pub` to send your **JSON** message.

### Your JSON must contain

- `temp`: (A number)
- `humidity`: (A number)
- `status`: (A string like "OK" or "Warning")

Did you succeed?

## Key take-aways

- **Decoupling:** The sender doesn't need to know who the listener is.
- **Orchestration:** Docker Compose makes complex setups repeatable.
- **JSON:** This is the standard language for all modern IoT data.

## Things to try if you want more challenges

1. **Subscribe to multiple topics** Create a subscriber that listens to multiple topics. And then try a publishing test on those. Tip: [MQTT Best Topic Practices](https://www.hivemq.com/blog/mqtt-essentials-part-5-mqtt-topics-best-practices/)
2. **Simulate a sensor stream** Real IoT systems send data continuously, not just once. Try to simulate that behavior. For this to work, you need to have earlier understanding of shell scripting or programming. We'll sort of do this in the next lab, so don't worry if you don't know how just yet.
