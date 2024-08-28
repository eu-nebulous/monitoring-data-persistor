import threading
from Constants import Constants
from exn import connector, core
from main.runtime.DataPersistor import Bootstrap

if __name__=="__main__":
    application_handler = Bootstrap()
    connector = connector.EXN('slovid', handler=application_handler,
                              consumers=[
                                  core.consumer.Consumer('monitoring', Constants.monitoring_broker_topic + '.>', topic=True,fqdn=True, handler=application_handler),
                              ],
                              url=Constants.broker_ip,
                              port=Constants.broker_port,
                              username=Constants.broker_username,
                              password=Constants.broker_password
                              )
    #connector.start()
    thread = threading.Thread(target=connector.start,args=())
    thread.start()