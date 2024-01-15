import json

import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision
from Constants import Constants
from influxdb_client.client.write_api import SYNCHRONOUS


def create_influxdb_bucket(application_name):
    bucket_name = Constants.application_name_prefix+application_name+"_bucket"

    # Replace with your actual values
    url = 'http://' + Constants.db_hostname + ':8086/api/v2/buckets'
    token = Constants.db_token
    headers = {
        'Authorization': 'Token {}'.format(token),
        'Content-Type': 'application/json'
    }
    data = {
        'name': bucket_name,
        'orgID': Constants.organization_id,
        'retentionRules': [
            {
                'type': 'expire',
                'everySeconds': 2592000 #30 days (30*24*3600)
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.status_code)
    print(response.json())
    return bucket_name


class InfluxDBConnector:

    def __init__(self):
        self.client = InfluxDBClient(url="http://"+Constants.db_hostname+":"+Constants.db_port, token=Constants.db_token, org=Constants.organization_name)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.influxdb_bucket_created = False
        self.bucket_name = "demo_bucket"
    def InfluxDBConnector(self):
        pass
    def write_data(self,data,application_name):
        if not self.influxdb_bucket_created:
            self.bucket_name = create_influxdb_bucket(application_name)
            self.influxdb_bucket_created = True

        self.write_api.write(bucket=self.bucket_name, org=Constants.organization_name, record=data, write_precision=WritePrecision.S)

    def get_data(self,metric_name):
        query_api = self.client.query_api()
        query = f"""from(bucket: "nebulous")
         |> range(start: -1m)
         |> filter(fn: (r) => r._measurement == "{metric_name}")"""
        tables = query_api.query(query, org=Constants.organization_name)

        for table in tables:
            for record in table.records:
                print(record)