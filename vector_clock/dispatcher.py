import pika
import json
import pika
import json
import time

local_clock = {'A': 0, 'B' : 0}
winner = None

def callback(ch, method, properties, body):
    global local_clock, winner

    data = json.loads(body)
    driver_id = data['driver']
    incoming_clock = data['clock']

    print(f"[Claim] Driver {driver_id} wants the order. (Vector: {incoming_clock})")

    if winner is None:
        winner = driver_id
        print(f"Driver {driver_id} has taken the order.")

        for key in incoming_clock:
            local_clock[key] = max(local_clock.get(key, 0), incoming_clock[key])
    else:
        print(f"Rejected driver {driver_id}.")

    payload = {
        "winner": winner,
        "server_clock": local_clock
    }

    ch.basic_publish(
        exchange='race_results', 
        routing_key='',   
        body=json.dumps(payload)
    )
    print(f"sent {payload}")

def run():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='claims_queue')
    channel.exchange_declare(exchange='race_results', exchange_type='fanout')
    
    print("Dispatcher Started.")
    print(f"Initial Clock: {local_clock}")

    input("Press ENTER to release the order...")

    channel.basic_publish(
        exchange='race_results', 
        routing_key='', 
        body=json.dumps({"status": "OPEN"})
    )
    print("Order released! Waiting for claims...")

    channel.basic_consume(queue='claims_queue', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    
run()