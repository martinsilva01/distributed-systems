import pika
import time
import json
import random
import threading
import logging

class LocationThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def get_location(self):
        longitude = random.randint(0,1000)
        lattitute = random.randint(0,1000)
        return f"Location:{longitude}, {lattitute}"

    def run(self):
        logger = logging.getLogger(__name__)
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange = 'delivery', exchange_type='topic')
        channel.queue_declare(queue='customer_updates')
        for i in range(5):
            channel.basic_publish(exchange='delivery', routing_key='driver.location.1', body = self.get_location())
            logger.info('[LocationThread] Sent Location.')
            time.sleep(1)
        connection.close()

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s', 
        handlers=[
            logging.FileHandler("driver.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    locationthread = LocationThread()
    locationthread.start()

    for i in range(10):
        logger.info('I am the Main Thread doing other stuff')
        time.sleep(1)

    locationthread.join()
    


    



main()
        
    
