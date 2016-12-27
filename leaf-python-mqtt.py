#!/usr/bin/python

import pycarwings2
import time
from ConfigParser import SafeConfigParser
import logging
import sys
import pprint
import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("emon/leaf/control/#")
  # leaf/control/ac/ 1 to turn on AC

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.publish("emonesp/test", "openevse connected");

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  
    print(msg.topic+" "+str(msg.payload))
    
    # If climate control messaage is received
    if msg.topic.rsplit('/',1)[0] == 'ac':
      if msg.payload == 1:
        print "Turing on climate control"
      if msg.payload == 0:
        print "Turing off climate control"
      
        

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set('emonpi', 'emonpimqtt2016');
client.connect("localhost", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
# client.publish("emon/leaf/status", "connected");
# client.loop_forever()









logging.basicConfig(stream=sys.stdout, level=logging.ERROR)


parser = SafeConfigParser()
candidates = [ 'config.ini', 'my_config.ini' ]
found = parser.read(candidates)

username = parser.get('get-leaf-info', 'username')
password = parser.get('get-leaf-info', 'password')

logging.debug("login = %s , password = %s" % ( username , password)  )

print "Prepare Session"
s = pycarwings2.Session(username, password , "NE")
print "Login..."
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

client.publish("emon/leaf/status/test", "publishing status")
time.sleep(1)
client.publish("emon/leaf/status/last_updated", leaf_info.answer["BatteryStatusRecords"]["NotificationDateAndTime"])
time.sleep(1)
client.publish("emon/leaf/status/battery_percent", leaf_info.battery_percent)
time.sleep(1)
client.publish("emon/leaf/status/charging_status", leaf_info.charging_status)
time.sleep(1)
client.publish("emon/leaf/status/connected", leaf_info.is_connected)

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
