import pika
import time
import json
import random


def get_location():
    longitude = random.randint(0,1000)
    lattitute = random.randint(0,1000)
    return f"Location:{longitude}, {lattitute}"

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange = 'delivery', exchange_type='topic')
    channel.queue_declare(queue='customer_updates')
    for i in range(5):
        channel.basic_publish(exchange='delivery', routing_key='driver.location.1', body = get_location())
        print("Sent Location")
        time.sleep(5)
    connection.close()


main()
        
    
