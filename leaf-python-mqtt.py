#!/usr/bin/python

import pycarwings2
import time
from ConfigParser import SafeConfigParser
import logging
import sys
import pprint
import paho.mqtt.client as mqtt
import schedule
from datetime import datetime
import os

config_file = 'config.ini'


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.info("Startup leaf-python-MQTT: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
config_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), config_file)

# Get login details from 'config.ini'
parser = SafeConfigParser()
if os.path.exists(config_file_path):
  logging.info("Loaded config file " + config_file_path)
  #candidates = [ 'config.ini', 'my_config.ini' ]
  candidates = config_file_path
  found = parser.read(candidates)
  username = parser.get('get-leaf-info', 'username')
  password = parser.get('get-leaf-info', 'password')
  mqtt_host = parser.get('get-leaf-info', 'mqtt_host')
  mqtt_port = parser.get('get-leaf-info', 'mqtt_port')
  mqtt_username = parser.get('get-leaf-info', 'mqtt_username')
  mqtt_password = parser.get('get-leaf-info', 'mqtt_password')
  mqtt_control_topic = parser.get('get-leaf-info', 'mqtt_control_topic')
  mqtt_status_topic =  parser.get('get-leaf-info', 'mqtt_status_topic')
else:
  logging.error("ERROR: Config file not found " + config_file_path)
  quit()
  

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  logging.info("Connected to MQTT with result code "+str(rc))
  logging.info("suscribing to leaf control topic" + mqtt_control_topic)
  client.subscribe(mqtt_control_topic + "/#")
  client.publish(mqtt_status_topic, "leaf status connected to MQTT");

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  
    logging.info(msg.topic+" "+str(msg.payload))
    
    # If climate control messaage is received
    if msg.topic.rsplit('/',1)[0] == 'climate':
      if msg.payload == 1:
        print "Turing on climate control"
      if msg.payload == 0:
        print "Turing off climate control"

client = mqtt.Client()
# Callback when MQTT is connected
client.on_connect = on_connect
# Callback when MQTT message is received
client.on_message = on_message
# Connect to MQTT
client.username_pw_set(mqtt_username, mqtt_password);
client.connect(mqtt_host, mqtt_port, 60)

def get_leaf_status():
  logging.debug("login = %s , password = %s" % ( username , password)  )
  print "Prepare Session"
  s = pycarwings2.Session(username, password , "NE")
  print "Login..."
  print datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  l = s.get_leaf()
  
  print "get_latest_battery_status"
  leaf_info = l.get_latest_battery_status()
  print "date %s" % leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"]
  print "date %s" % leaf_info.answer["BatteryStatusRecords"]["NotificationDateAndTime"]
  print "battery_capacity2 %s" % leaf_info.answer["BatteryStatusRecords"]["BatteryStatus"]["BatteryCapacity"]
  
  print "battery_capacity %s" % leaf_info.battery_capacity
  print "charging_status %s" % leaf_info.charging_status
  print "battery_capacity %s" % leaf_info.battery_capacity
  print "battery_remaining_amount %s" % leaf_info.battery_remaining_amount
  print "charging_status %s" % leaf_info.charging_status
  print "is_charging %s" % leaf_info.is_charging
  print "is_quick_charging %s" % leaf_info.is_quick_charging
  print "plugin_state %s" % leaf_info.plugin_state
  print "is_connected %s" % leaf_info.is_connected
  print "is_connected_to_quick_charger %s" % leaf_info.is_connected_to_quick_charger
  print "time_to_full_trickle %s" % leaf_info.time_to_full_trickle
  print "time_to_full_l2 %s" % leaf_info.time_to_full_l2
  print "time_to_full_l2_6kw %s" % leaf_info.time_to_full_l2_6kw
  print "leaf_info.battery_percent %s" % leaf_info.battery_percent
  

  client.publish(mqtt_status_topic + "/last_updated", leaf_info.answer["BatteryStatusRecords"]["NotificationDateAndTime"])
  time.sleep(1)
  client.publish(mqtt_status_topic + "/battery_percent", leaf_info.battery_percent)
  time.sleep(1)
  client.publish(mqtt_status_topic + "/charging_status", leaf_info.charging_status)
  time.sleep(1)
  
  if leaf_info.is_connected == True:
    client.publish(mqtt_status_topic + "/connected", "Yes")
  elif leaf_info.is_connected == False:
    client.publish(mqtt_status_topic + "/connected", "No")
  else:
    client.publish(mqtt_status_topic + "/connected", leaf_info.is_connected)



schedule.every(1).minutes.do(get_leaf_status)

while True:
    schedule.run_pending()
    time.sleep(1)
    
    # MQTT loop
    # client.loop_forever()

    
    
    

# result_key = l.request_update()
# print "start sleep 10"
# time.sleep(10) # sleep 60 seconds to give request time to process
# print "end sleep 10"
# battery_status = l.get_status_from_update(result_key)
# while battery_status is None:
# 	print "not update"
#         time.sleep(10)
# 	battery_status = l.get_status_from_update(result_key)

# pprint.pprint(battery_status.answer)

#result_key = l.start_climate_control()
#time.sleep(60)
#start_cc_result = l.get_start_climate_control_result(result_key)

#result_key = l.stop_climate_control()
#time.sleep(60)
#stop_cc_result = l.get_stop_climate_control_result(result_key)
