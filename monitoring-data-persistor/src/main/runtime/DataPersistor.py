import logging
import sys
import threading
from time import sleep

from jproperties import Properties

from influxdb_client import Point, WritePrecision

import exn
from main.runtime import State
from main.runtime.Constants import Constants
from main.runtime.InfluxDBConnector import InfluxDBConnector
from exn import connector, core
from exn.core.handler import Handler
from exn.handler.connector_handler import ConnectorHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('main.exn.connector').setLevel(logging.DEBUG)


class Bootstrap(ConnectorHandler):
    pass
class ConsumerHandler(Handler):
    influx_connector = None
    application_name = ""
    def __init__(self,application_name):
        self.application_name = application_name
        self.influx_connector = InfluxDBConnector()
    def on_message(self, key, address, body, context, **kwargs):
        logging.info(f"Received {key} => {address}")
        if ((str(address)).startswith(Constants.monitoring_prefix) and not (str(address)).endswith(Constants.metric_list_topic)):
            logging.info("New monitoring data arrived at topic "+address)
            logging.info(body)
            if ((str(address).split(".")[-2]) == "realtime"):
                point = Point(str(address).split(".")[-1]).field("metricValue",body["metricValue"]).tag("level",body["level"]).tag("application_name",self.application_name)
                point.time(body["timestamp"],write_precision=WritePrecision.MS)
                logging.info("Writing new real-time monitoring data to Influx DB")
                self.influx_connector.write_data(point,self.application_name)
            elif ((str(address).split(".")[-2]) == "predicted"):
                point = Point("_predicted_"+str(address).split(".")[-1]).field("metricValue",body["metricValue"]).tag("probability",body["probability"]).tag("predictionTime",body["predictionTime"]).tag("confidence_interval",body["confidence_interval"]).tag("application_name",self.application_name)
                point.time(body["timestamp"],write_precision=WritePrecision.MS)
                logging.info("Writing new predicted monitoring data to Influx DB")
                self.influx_connector.write_data(point,self.application_name)

class GenericConsumerHandler(Handler):
    connector_thread = None
    #initialized_connector = None
    application_consumer_handler_connectors = {} #dictionary in which keys are applications and values are the consumer handlers.
    application_threads = {}

    def GenericConsumerHandler(self):
        pass
        #if self.connector_thread is not None:
            #self.initialized_connector.stop()
    def on_message(self, key, address, body, context, **kwargs):

        if (str(address)).startswith(Constants.monitoring_prefix+Constants.metric_list_topic):
            need_to_restart_connector = False
            application_name = body["name"]
            message_version = body["version"]
            logging.info("New metrics list message for application "+application_name + " - registering new connector")
        
            if (application_name in State.metric_list_message_versions and message_version > State.metric_list_message_versions[application_name]):
                logging.info("Stopping the old connector (as a new message version arrived)...")
                State.metric_list_message_versions[application_name] = message_version
                need_to_restart_connector = True
            elif not (application_name in State.metric_list_message_versions):
                logging.info("Starting a new connector...")
                State.metric_list_message_versions[application_name] = message_version
                need_to_restart_connector = True
            else:
                logging.info("No need to stop the old existing connector, as the message version has not been updated...")

            while (need_to_restart_connector):
                try:
                    need_to_restart_connector = False
                    if (application_name in self.application_consumer_handler_connectors.keys()):
                        self.application_consumer_handler_connectors[application_name].stop()
                    logging.info("Attempting to register new connector...")
                    application_handler = ConsumerHandler(application_name=application_name)
                    
                    self.application_consumer_handler_connectors[application_name] = exn.connector.EXN(
                        Constants.data_persistor_name + "-" + application_name, handler=Bootstrap(),
                        consumers=[
                            core.consumer.Consumer('monitoring-data-persistor-realtime'+application_name,
                                                   Constants.monitoring_broker_topic + '.realtime.>',
                                                   application=application_name,
                                                   topic=True,
                                                   fqdn=True,
                                                   handler=application_handler),
                            core.consumer.Consumer('monitoring-data-persistor-predicted'+application_name,
                                                   Constants.monitoring_broker_topic + '.predicted.>',
                                                   application=application_name,
                                                   topic=True,
                                                   fqdn=True,
                                                   handler=application_handler
                                                   )
                        ],
                        url=Constants.broker_ip,
                        port=Constants.broker_port,
                        username=Constants.broker_username,
                        password=Constants.broker_password
                    )
                    logging.info("Connector ready to be registered")
                    #connector.start()
                    #self.application_consumer_handler_connectors[application_name] = self.initialized_connector
                    #self.application_consumer_handler_connectors[application_name].start()
                    logging.info(f"Application specific connector registered for application {application_name}")
                    #self.initialized_connector.start()
        
                    #If threading support is explicitly required, uncomment these lines
                    self.application_threads[application_name] = threading.Thread(target=self.application_consumer_handler_connectors[application_name].start,args=())
                    self.application_threads[application_name].start()
                    logging.info(f"Application specific connector started for application {application_name}")
                    self.application_threads[application_name].join()
                    #connector_thread = threading.Thread(target=self.application_consumer_handler_connectors[application_name].start,args=())
                    #connector_thread.start()
                    #connector_thread.join()
                except Exception as e:
                    logging.error("Exception occurred while trying to re-create connector for application %s, will retry in 5 seconds",application_name)
                    logging.exception(e)
                    need_to_restart_connector = True
                    sleep(5)


def update_properties(configuration_file_location):
    p = Properties()
    with open(configuration_file_location, "rb") as f:
        p.load(f, "utf-8")
        Constants.broker_ip, metadata = p["broker_ip"]
        Constants.broker_port, metadata = p["broker_port"]
        Constants.broker_username, metadata = p["broker_username"]
        Constants.broker_password, metadata = p["broker_password"]
        Constants.monitoring_broker_topic, metadata = p["monitoring_broker_topic"]
        Constants.influxdb_hostname, metadata = p["influxdb_hostname"]
        Constants.influxdb_password, metadata = p["influxdb_password"]
        Constants.influxdb_username, metadata = p["influxdb_username"]
        Constants.influxdb_token, metadata = p["influxdb_token"]
        Constants.influxdb_organization_name,metadata = p["influxdb_organization_name"]

def main():
    Constants.configuration_file_location = sys.argv[1]
    update_properties(Constants.configuration_file_location)
    component_handler = Bootstrap()

    connector_instance = connector.EXN(Constants.data_persistor_name, handler=component_handler,
                                       consumers=[
                                  core.consumer.Consumer('monitoring_data', Constants.monitoring_broker_topic + '.>', topic=True, fqdn=True, handler=GenericConsumerHandler()),
                              ],
                                       url=Constants.broker_ip,
                                       port=Constants.broker_port,
                                       username=Constants.broker_username,
                                       password=Constants.broker_password
                              )
    #connector.start()
    thread = threading.Thread(target=connector_instance.start,args=())
    thread.start()

    print("Waiting for messages at the metric list topic, in order to start receiving applications")

if __name__ == "__main__":
    main()