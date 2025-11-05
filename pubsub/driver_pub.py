import pika
import time
import json
import random
import threading

class LocationThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def get_location(self):
        longitude = random.randint(0,1000)
        lattitute = random.randint(0,1000)
        return f"Location:{longitude}, {lattitute}"

    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange = 'delivery', exchange_type='topic')
        channel.queue_declare(queue='customer_updates')
        for i in range(5):
            channel.basic_publish(exchange='delivery', routing_key='driver.location.1', body = self.get_location())
            print("Sent Location")
            time.sleep(1)
        connection.close()

def main():
    locationthread = LocationThread()
    locationthread.start()

    for i in range(5):
        print("Im still doing other stuff")
        time.sleep(1)

    locationthread.join()
    


    



main()
        
    
