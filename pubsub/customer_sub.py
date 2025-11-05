import pika
import time
import json
import random
import threading
import queue

class SubscriberThread(threading.Thread):
    
    def __init__(self, message_queue):
        super().__init__()
        self.message_queue = message_queue


    def callback(self, ch, method, properties, body):
        message = body.decode('utf-8')
        self.message_queue.put(message)


    def run(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        channel = connection.channel()
        channel.exchange_declare(exchange = 'delivery', exchange_type='topic')
        channel.queue_declare(queue='customer_updates')
        channel.queue_bind(exchange = 'delivery', queue = 'customer_updates', routing_key = 'driver.location.1')

        print('Waiting for logs.')


        channel.basic_consume(queue='customer_updates', on_message_callback=self.callback, auto_ack=True)

        channel.start_consuming()

        time.sleep(40)

        connection.close()

def main():
    message_queue = queue.Queue()

    location_thread = SubscriberThread(message_queue)
    location_thread.start()

    while True:
        message = message_queue.get()
        print(message)
        time.sleep(2)
