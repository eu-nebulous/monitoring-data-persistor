import time

from influxdb_client import Point, WritePrecision
import logging

from main.runtime.InfluxDBConnector import InfluxDBConnector



def main():
    address = "eu.nebulouscloud.monitoring.realtime.cpu_usage"
    influx_connector  = InfluxDBConnector()
    body={
        "metricValue": 100.0,
        "level":3,
        "timestamp": time.time()
    }
    
    application_name = "andreas-2cf2-49bd-bf65-5ad71bb91890"
    point = Point(str(address).split(".")[-1]).field("metricValue",body["metricValue"]).tag("level",body["level"]).tag("application_name",application_name)
    
    for data_point_counter in range(1000*1000*1000):    
        point.time(int(1000*time.time()),write_precision=WritePrecision.MS)
        influx_connector.write_data(point,application_name)
        print(f"Data {data_point_counter} written")
        time.sleep(0.1)

if __name__ == "__main__":
    main()