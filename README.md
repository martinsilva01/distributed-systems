# distributed-systems
This repository demonstrates a simple interprocess communication (IPC) setup between a client device and a printer daemon using UNIX sockets, alongside a lightweight Flask REST API serving restaurant data and food images.

## IPC Directory
`utils/utils.py`
  - Utility module providing helper functions for validating lists of strings:
    - isStringList(lst): Checks if all elements in a list are strings.
    - equalLengthList(lst): Checks if all strings in a list are of equal length and returns that length (or -1 if not).

`Receipt.py`
  - Defines the Receipt class responsible for:
    - Validating and formatting receipt data.
    - Managing receipt dimensions (max_height, max_width).
    - Combining header and body sections into a printable receipt format.

`client_device.py`
    - Simulates a client device sending receipt data to a printer daemon via a UNIX socket.
    - Builds a receipt using the Receipt class.
    - Connects to /tmp/print.sock and sends formatted text periodically.

`printer_daemon.py`
  - Acts as the receipt printer daemon:
  - Listens on /tmp/print.sock for incoming connections.
  - Prints received data to the console, simulating receipt output.

## API Directory
`server.py`
  - Flask-based REST API providing:
    - `/restaurant` → Returns a JSON list of restaurant names.
    - `/food/<imageName>` → Serves corresponding food images from the food/ directory.

`client.py`
  - Simple API client that:
    - Fetches and displays the restaurant list.
    - Requests an image (e.g., cheeseburger.jpg) from the server and opens it with Pillow.

## Dependencies
Required Libraries:
```
redis
fastapi
flask
requests
Pillow
```

In order to run this project via git:

```
~/: git clone https://github.com/martinsilva01/distributed-systems
~/: cd distributed-systems/

### Optionally ###
~/distributed-systems/: python3 -m venv .venv
~/distributed-systems/: source .venv/bin/activate
(.venv) ~/distributed-systems/: pip install -r requirements.txt
```

### IPC:
Terminal 1:
```
cd ipc
python3 printer_daemon.py
```
Terminal 2:
```
cd ipc
python3 client_device.py
```

`printer_daemon.py` will wait for a connection and accept receipt data via UNIX socket from `client_device.py` 

### API:
Terminal 1:
```
cd api
python3 server.py
```
Terminal 2:
```
cd api
python3 client.py
```

`server.py` will act as a REST API which accepts requests to `/restaurant` and `/food`.
Use `client.py` to test the API or send requests manually using curl.


### PUB SUB directory

# Requirements and Dependecies
Python package: pika
External service: A RabbitMQ server.  We used Docker.

# Component purpose
This section shows a Publish-Subscribe pattern using RabbitMQ.  It uses a topic exchange for routing.  

driver_pub.py:  This is the publisher.  It connects to RabbitMQ and declares a topic named delivery.  Every 5 seconds, it publishes a random location message using the routing key, "driver.location.1"

customer_sub.py:  This is the subscriber.It connects to RabbitMQ, it uses the delivery topic exchange.  It specifically listens for messages matching the driver.location.1 routing key.  

# How to run
Start rabbitmq in docker: Open a terminal and run the following command.
docker run -d --hostname my-rabbit --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

Start the subscriber: Open a second terminal and run the following command.
python3 pubsub/customer_sub.py

Start the publisher: Open a third terminal and run the following command.
python3 pubsub/driver_pub.py