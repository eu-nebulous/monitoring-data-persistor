import logging
import threading
import time,random
import traceback

from exn import connector, core


class Bootstrap(connector.connector_handler.ConnectorHandler):
    pass


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('exn.connector').setLevel(logging.DEBUG)

application_name = "_Application1"
metric_list = ["cpu_usage","ram_usage"]
publisher_dict = {}
publisher_list = []
for metric in metric_list:
    new_publisher = (core.publisher.Publisher("demopublisher_"+metric,"eu.nebulouscloud.monitoring."+metric,topic=True,fqdn=True))
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
        try:
            publisher_dict[metric_name].send(body=message,application=application_name)
            if counter%50==0:
                print("Sending message "+str(counter))
            counter = counter +1
        except Exception as e:
            print(traceback.format_exc())

