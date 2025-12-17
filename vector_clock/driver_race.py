import pika
import json
import sys

driver_id = sys.argv[1]

def run_race():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='race_results', exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue
    channel.queue_bind(exchange='race_results', queue=callback_queue)
    
    channel.queue_declare(queue='claims_queue')

    print(f"Driver {driver_id} is ready. Waiting for order...")

    my_vector = {'A': 0, 'B': 0}
    my_vector[driver_id] += 1
    
    def on_event(ch, method, props, body):
        data = json.loads(body)
        
        if data.get('status') == 'OPEN':
            payload = {
                "driver": driver_id,
                "clock": my_vector
            }
            channel.basic_publish(
                exchange='', 
                routing_key='claims_queue', 
                body=json.dumps(payload)
            )
            print(f"Sent CLAIM: {my_vector}")

        elif 'winner' in data:
            winner = data['winner']
            server_clock = data['server_clock']
            
            if winner == driver_id:
                print(f"\nThe server announced I ({winner}) took the order")
                print(f"Server Clock Synced: {server_clock}")
            else:
                print(f"\nThe server announced I did not take the order.")
                print(f"Server Clock is {server_clock}")
            
            channel.stop_consuming()

    channel.basic_consume(queue=callback_queue, on_message_callback=on_event, auto_ack=True)
    channel.start_consuming()
    
    connection.close()

run_race()