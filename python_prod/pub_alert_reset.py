environment = "prod"

import time  
import paho.mqtt.client as mqtt
from datetime import datetime

reset = 1

def debuglog(debug_output):
    with open("/home/pi/home_iot/python_"+environment+"/debug.log", 'a') as file1:
        file1.write(str(datetime.now())+" \t"+debug_output+" \n")

def on_connect(client, userdata, flags, rc): 
   debuglog("Connected with result code " + str(rc))    
   client.subscribe('pi/pub_alert_reset')
   client.publish('pi/pub_alert_reset', reset)
   debuglog("Alert reset PUBLISHED")

def on_message(client, userdata, msg):
   if msg.topic == 'pi/pub_alert_reset':
        debuglog("Alert reset self subscribed")
        debuglog(msg.topic+" "+str( msg.payload))

client = mqtt.Client() 
client.on_connect = on_connect
client.on_message = on_message
client.connect('192.168.1.22', 1883, 60) 
client.loop_start()
debuglog('Script is running, press Ctrl-C to quit...') 
while True:
   time.sleep(2)
   break
   