import logging
import threading
import time,random

from influxdb_client import Point, WritePrecision, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from Constants import Constants
from InfluxDBConnector import InfluxDBConnector
from main.exn import connector, core
from datetime import datetime


class Bootstrap(connector.connector_handler.ConnectorHandler):
    pass


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('main.exn.connector').setLevel(logging.DEBUG)


metric_list = ["cpu_usage","ram_usage"]
publisher_dict = {}
publisher_list = []
for metric in metric_list:
    new_publisher = (core.publisher.Publisher("slovid","monitoring."+metric,topic=True))
    publisher_dict[metric]= new_publisher
    publisher_list.append(new_publisher)

connector = connector.EXN('slovid', handler=Bootstrap(),
                          consumers=[],
                          publishers=publisher_list,
                          url="localhost",
                          port="5672",
                          username="admin",
                          password="admin",
                          enable_health=False
                          )
#connector.start()
thread = threading.Thread(target=connector.start,args=())
thread.start()
time.sleep(5)
time_to_generate_time_for = 10*3600
frequency = 5

for metric_name in metric_list:
    current_time = int(time.time())
    counter = 0
    print("Data for "+metric_name)
    for time_point in range(current_time-time_to_generate_time_for,current_time,frequency):
        random_value = random.uniform(0,100)
        message = {
            "metricValue": random_value,
            "level": 1,
            "component_id":"wordpress_1",
            "timestamp": time_point
        }
        publisher_dict[metric_name].send(body=message)
        if counter%50==0:
            print("Sending message "+str(counter))
        counter = counter +1

