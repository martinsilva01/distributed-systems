import pika
import time
import json
import random
import threading
import queue
import logging

class SubscriberThread(threading.Thread):
    
    def __init__(self, message_queue):
        super().__init__()
        self.message_queue = message_queue
        self.daemon = True
        self.local_clock ={'driver' : 0, 'customer':0}


    def callback(self, ch, method, properties, body):
        message = json.loads(body.decode('utf-8'))
        received_clock = message['vector_clock']
        if received_clock['driver'] > self.local_clock['driver']:
            self.local_clock['driver'] = received_clock['driver']
            self.local_clock['customer'] += 1
            display_msg = (f"Loc: {message['longitude']},{message['latitude']} | Global Time: {self.local_clock}")
            self.message_queue.put(display_msg)
        else:
            logging.getLogger(__name__).warning(
                f"[SubscriberThread] Ignored out of order message"
            )


    def run(self):
        try: 
            logger = logging.getLogger(__name__)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost'))

            channel = connection.channel()
            channel.exchange_declare(exchange = 'delivery', exchange_type='topic')
            channel.queue_declare(queue='customer_updates')
            channel.queue_bind(exchange = 'delivery', queue = 'customer_updates', routing_key = 'driver.location.1')

            print('Waiting for logs.')


            channel.basic_consume(queue='customer_updates', on_message_callback=self.callback, auto_ack=True)

            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            logger.error((f"[SubscriberThread] Connection failed: {e}"))
        except Exception as e:
            logger.error(f"[SubscriberThread] An error occurred: {e}")
        time.sleep(40)

        connection.close()

def main():
    logging.basicConfig(
        level = logging.INFO,
        format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s', 
        handlers=[
            logging.FileHandler("subscriber_node_failure.log"), 
            logging.StreamHandler() 
        ]
    )
    logger = logging.getLogger(__name__)
    message_queue = queue.Queue()

    location_thread = SubscriberThread(message_queue)
    location_thread.start()

    logger.info('[MainThread] Waiting for messages...')
    try:    
        while True:

            try:
                message = message_queue.get_nowait()
                logger.info(f'Processed: {message}')
            except queue.Empty:
                pass
            logger.info('I am the main thread still doing stuff')
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n[MainThread] Shutting down.")



main()

#docker run -d --hostname my-rabbit --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management