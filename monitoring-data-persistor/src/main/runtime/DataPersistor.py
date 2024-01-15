import logging
import os
import sys
import threading
import time
from jproperties import Properties

from influxdb_client import Point, WritePrecision, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from Constants import Constants
from InfluxDBConnector import InfluxDBConnector
from main.exn import connector, core
from main.exn.handler.connector_handler import ConnectorHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('main.exn.connector').setLevel(logging.DEBUG)


class Bootstrap(ConnectorHandler):

    influx_connector = InfluxDBConnector()
    def on_message(self, key, address, body, context, **kwargs):
        logging.info(f"Received {key} => {address}")
        application_name = "default_application"
        if (str(address)).startswith(Constants.monitoring_prefix):
            logging.info("New monitoring data arrived at topic "+address)
            logging.info(body)
            point = Point(str(address).split(".")[-1]).field("metricValue",body["metricValue"]).tag("level",body["level"]).tag("component_id",body["component_id"]).tag("application_name",application_name)
            point.time(body["timestamp"],write_precision=WritePrecision.S)
            self.influx_connector.write_data(point)
        else:
            print("Address is "+str(address)+", but it was expected for it to start with " + Constants.monitoring_prefix)


def update_properties(configuration_file_location):
    p = Properties()
    with open(Constants.configuration_file_location, "rb") as f:
        p.load(f, "utf-8")
        Constants.broker_ip, metadata = p["broker_ip"]
        Constants.broker_port, metadata = p["broker_port"]
        Constants.broker_username, metadata = p["broker_username"]
        Constants.broker_password, metadata = p["broker_password"]
        Constants.monitoring_broker_topic, metadata = p["monitoring_broker_topic"]

if __name__ == "__main__":
    Constants.configuration_file_location = sys.argv[1]
    update_properties(Constants.configuration_file_location)
    application_handler = Bootstrap()
    connector = connector.EXN('slovid', handler=application_handler,
                              consumers=[
                                  core.consumer.Consumer('monitoring', Constants.monitoring_broker_topic + '.>', topic=True, handler=application_handler),
                              ],
                              url=Constants.broker_ip,
                              port=Constants.broker_port,
                              username=Constants.broker_username,
                              password=Constants.broker_password
                              )
    #connector.start()
    thread = threading.Thread(target=connector.start,args=())
    thread.start()

