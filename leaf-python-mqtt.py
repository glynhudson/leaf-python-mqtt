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
  nissan_region_code = parser.get('get-leaf-info', 'nissan_region_code')
  GET_UPDATE_INTERVAL = parser.get('get-leaf-info', 'api_update_interval_min')
  logging.info("updating data from API every " + GET_UPDATE_INTERVAL +"min")
else:
  logging.error("ERROR: Config file not found " + config_file_path)
  quit()
  

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  logging.info("Connected to MQTT host " + mqtt_host + " with result code "+str(rc))
  logging.info("Suscribing to leaf control topic: " + mqtt_control_topic)
  client.subscribe(mqtt_control_topic + "/#")
  logging.info("Publishing to leaf status topic: " + mqtt_status_topic)
  client.publish(mqtt_status_topic, "MQTT connected");

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  
    logging.info(msg.topic+" "+str(msg.payload))

    control_subtopic = msg.topic.rsplit('/',1)[1]
    control_message = msg.payload
    logging.info("control sub-topic: " + control_subtopic)
    logging.info("control message: " + control_message)

    # If climate control messaage is received mqtt_control_topic/climate
    if control_subtopic == 'climate':
      logging.info('Climate control command received: ' + control_message)
      
      if control_message == '1':
        climate_control(1)

      if control_message == '0':
        climate_control(0)
        
    # If climate control messaage is received on mqtt_control_topic/update
    if control_subtopic == 'update':
      logging.info('Update control command received: ' + control_message)
      if control_message == '1':
        get_leaf_update()
        time.sleep(30)
        get_leaf_status()
        
client = mqtt.Client()
# Callback when MQTT is connected
client.on_connect = on_connect
# Callback when MQTT message is received
client.on_message = on_message
# Connect to MQTT
client.username_pw_set(mqtt_username, mqtt_password);
client.connect(mqtt_host, mqtt_port, 60)
client.publish(mqtt_status_topic, "Connecting to MQTT host " + mqtt_host);
# Non-blocking MQTT subscription loop
client.loop_start()




def climate_control(climate_control_instruction):
  logging.debug("login = %s , password = %s" % ( username , password)  )
  logging.info("Prepare Session climate control update")
  s = pycarwings2.Session(username, password , "NE")
  logging.info("Login...")
  logging.info(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
  l = s.get_leaf()
  
  if climate_control_instruction == 1:
    logging.info("Turning on climate control..wait 60s")
    result_key = l.start_climate_control()
    time.sleep(60)
    start_cc_result = l.get_start_climate_control_result(result_key)
    logging.info(start_cc_result)

  if climate_control_instruction == 0:
    logging.info("Turning off climate control..wait 60s")
    result_key = l.stop_climate_control()
    time.sleep(60)
    stop_cc_result = l.get_stop_climate_control_result(result_key)
    logging.info(stop_cc_result)

  

def get_leaf_update():
  logging.debug("login = %s , password = %s" % ( username , password)  )
  logging.info("Prepare Session get car update")
  s = pycarwings2.Session(username, password , "NE")
  logging.info("Login...")
  logging.info(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
  try:
    l = s.get_leaf()
  except:
    logging.error("CarWings API error")
  logging.info("Requesting update from car..wait 30s")
  try:
    result_key = l.request_update()
  except:
    logging.error("ERROR: no responce from car update")
  time.sleep(30)
  battery_status = l.get_status_from_update(result_key)
  
  while battery_status is None:
    logging.error("ERROR: no responce from car")
    time.sleep(10)
    battery_status = l.get_status_from_update(result_key)
  
  leaf_info = l.get_latest_battery_status()

  
def get_leaf_status():
  logging.debug("login = %s , password = %s" % ( username , password) )
  logging.info("Prepare Session")
  s = pycarwings2.Session(username, password , nissan_region_code)
  logging.info("Login...")
  logging.info("Start update time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
  
  try:
    l = s.get_leaf()
  except:
    logging.error("CarWings API error")
  
  logging.info("get_latest_battery_status")
  
  leaf_info = l.get_latest_battery_status()
  
  logging.info("date %s" % leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"])
  logging.info("date %s" % leaf_info.answer["BatteryStatusRecords"]["NotificationDateAndTime"])
  logging.info("battery_capacity2 %s" % leaf_info.answer["BatteryStatusRecords"]["BatteryStatus"]["BatteryCapacity"])
  logging.info("battery_capacity %s" % leaf_info.battery_capacity)
  logging.info("charging_status %s" % leaf_info.charging_status)
  logging.info("battery_capacity %s" % leaf_info.battery_capacity)
  logging.info("battery_remaining_amount %s" % leaf_info.battery_remaining_amount)
  logging.info("charging_status %s" % leaf_info.charging_status)
  logging.info("is_charging %s" % leaf_info.is_charging)
  logging.info("is_quick_charging %s" % leaf_info.is_quick_charging)
  logging.info("plugin_state %s" % leaf_info.plugin_state)
  logging.info("is_connected %s" % leaf_info.is_connected)
  logging.info("is_connected_to_quick_charger %s" % leaf_info.is_connected_to_quick_charger)
  logging.info("time_to_full_trickle %s" % leaf_info.time_to_full_trickle)
  logging.info("time_to_full_l2 %s" % leaf_info.time_to_full_l2)
  logging.info("time_to_full_l2_6kw %s" % leaf_info.time_to_full_l2_6kw)
  logging.info("leaf_info.battery_percent %s" % leaf_info.battery_percent)
  
  # logging.info("getting climate update")
  # climate = l.get_latest_hvac_status()
  # pprint.pprint(climate)

  logging.info("publishing to MQTT base status topic: " + mqtt_status_topic)
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
  logging.info("End update time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
  logging.info("Schedule API update every " + GET_UPDATE_INTERVAL + "min")



# Run on first time
get_leaf_status()

# Then schedule
logging.info("Schedule API update every " + GET_UPDATE_INTERVAL + "min")
schedule.every(int(GET_UPDATE_INTERVAL)).minutes.do(get_leaf_status)

while True:
    schedule.run_pending()
    time.sleep(1)