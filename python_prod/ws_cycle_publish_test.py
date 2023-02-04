environment = "prod"

import time  
from datetime import datetime
import paho.mqtt.client as mqtt
import traceback
import logging
import sys

reset_cycle = 1

def debuglog(debug_output):
    with open("/home/pi/home_iot/python_"+environment+"/debug.log", 'a') as file1:
        file1.write(str(datetime.now())+" \t"+debug_output+" \n")

def on_connect(client, userdata, flags, rc): 
   debuglog("Connected with result code " + str(rc)) 
 
   client.subscribe('pi/pub_cycle_reset')
   client.publish('pi/pub_cycle_reset', reset_cycle)
   debuglog("Cycle reset PUBLISHED")

   client.subscribe("pi/ws/switch") 
   client.publish('pi/ws/switch', "TEST")
   client.publish('pi/ws/switch', "SWITCH")
   client.publish('pi/ws/switch', "SWITCH")
   client.publish('pi/ws/switch', "SWITCH")
   client.publish('pi/ws/switch', "SWITCH")
   client.publish('pi/ws/switch', "SWITCH")
   client.publish('pi/ws/switch', "SWITCH")
   client.publish('pi/ws/switch', "SWITCH")
   client.publish('pi/ws/switch', "SWITCH")  
   client.publish('pi/ws/switch', "SWITCH")
   client.publish('pi/ws/switch', "SWITCH")
   client.publish('pi/ws/switch', "SWITCH")
   client.publish('pi/ws/switch', "SWITCH")   
   
   debuglog("Published TEST SIGNALS: full regen cycle + 2 for error alert test")

def on_message(client, userdata, msg):
   if msg.topic == 'pi/pub_alert_reset':
        debuglog("Cycle reset self subscribed")
        debuglog(msg.topic+" "+str( msg.payload))
        
   if msg.topic == 'pi/ws/switch':
        debuglog("Got switch signal self check")
        debuglog(msg.topic+" "+str( msg.payload))

client = mqtt.Client() 
client.on_connect = on_connect
client.on_message = on_message
client.connect('192.168.1.22', 1883, 60) 

client.loop_start()
while True:
    time.sleep(2)
    break