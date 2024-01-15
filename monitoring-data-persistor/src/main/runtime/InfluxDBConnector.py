from influxdb_client import InfluxDBClient, Point, WritePrecision
from Constants import Constants
from influxdb_client.client.write_api import SYNCHRONOUS



class InfluxDBConnector:
    client = InfluxDBClient(url="http://"+Constants.db_hostname+":"+Constants.db_port, token=Constants.db_token, org=Constants.organization_name)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    def InfluxDBConnector(self):
        pass
    def write_data(self,data):
        self.write_api.write(bucket=Constants.bucket_name, org=Constants.organization_name, record=data, write_precision=WritePrecision.S)

    def get_data(self):
        query_api = self.client.query_api()
        query = """from(bucket: "nebulous")
         |> range(start: -1m)
         |> filter(fn: (r) => r._measurement == "temperature")"""
        tables = query_api.query(query, org=Constants.organization_name)

        for table in tables:
            for record in table.records:
                print(record)