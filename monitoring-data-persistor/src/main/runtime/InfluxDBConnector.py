import json,logging

import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision
from main.runtime.Constants import Constants
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
    logging.info("The response code for our attempt in trying to create the bucket is "+str(response.status_code))
    logging.info("The response json for our attempt in trying to create the bucket is "+str(response.json()))
    return bucket_name


class InfluxDBConnector:
    applications_with_influxdb_bucket_created  = []
    def __init__(self):
        self.client = InfluxDBClient(url="http://"+Constants.db_hostname+":"+Constants.db_port, token=Constants.db_token, org=Constants.organization_name)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        #self.influxdb_bucket_created[application_name] = False
        self.bucket_name = "demo_bucket"
    def InfluxDBConnector(self):
        pass
    def write_data(self,data,application_name):
        if not application_name in self.applications_with_influxdb_bucket_created:
            org_api = self.client.organizations_api()
            # List all organizations
            organizations = org_api.find_organizations()

            # Find the organization by name and print its ID
            for org in organizations:
                if org.name == Constants.organization_name:
                    logging.info(f"Organization Name: {org.name}, ID: {org.id}")
                    Constants.organization_id = org.id
                    break

            logging.info("The influxdb bucket was reported as not created")
            self.bucket_name = create_influxdb_bucket(application_name)
            self.applications_with_influxdb_bucket_created.append(application_name)
        else:
            logging.info("The influxdb bucket was reported as created")
        logging.info(f"The data point is {data}")
        self.write_api.write(bucket=self.bucket_name, org=Constants.organization_name, record=data, write_precision=WritePrecision.S)
        logging.info("The data point has been written!")

    def get_data(self,metric_name):
        query_api = self.client.query_api()
        query = f"""from(bucket: "nebulous")
         |> range(start: -1m)
         |> filter(fn: (r) => r._measurement == "{metric_name}")"""
        tables = query_api.query(query, org=Constants.organization_name)

        for table in tables:
            for record in table.records:
                print(record)