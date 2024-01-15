from datetime import datetime
from Constants import Constants
from InfluxDBConnector import InfluxDBConnector
import time

## This utility assumes that the database has been filled with values for cpu usage and ram usage

metric_names = ["cpu_usage","ram_usage"]
for metric_name in metric_names:
    time_interval_to_get_data_for = "10h"
    print_data_from_db = True
    query_string = 'from(bucket: "'+Constants.bucket_name+'")  |> range(start:-'+time_interval_to_get_data_for+')  |> filter(fn: (r) => r["_measurement"] == "'+metric_name+'")'
    influx_connector = InfluxDBConnector()
    for counter in range(10):
        print("performing query")
        current_time = time.time()
        result = influx_connector.client.query_api().query(query_string, Constants.organization_name)
        elapsed_time = time.time()-current_time
        print("performed query, it took "+str(elapsed_time) + " seconds")
        #print(result.to_values())
        for table in result:
            #print header row
            print("Timestamp,ems_time,"+metric_name)
            for record in table.records:
                dt = datetime.fromisoformat(str(record.get_time()))
                epoch_time = int(dt.timestamp())
                metric_value = record.get_value()
                if(print_data_from_db):
                    print(str(epoch_time)+","+str(epoch_time)+","+str(metric_value))
        time.sleep(10)


