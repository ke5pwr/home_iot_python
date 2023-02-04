environment = "prod"

import time  
import paho.mqtt.client as mqtt
from datetime import datetime

interval = 60

def debuglog(debug_output):
    with open("/home/pi/home_iot/python_"+environment+"/debug.log", 'a') as file1:
        file1.write(str(datetime.now())+" \t"+debug_output+" \n")

def init_interval_data(init_input):
    with open("/home/pi/home_iot/python_"+environment+"/init_interval.py", 'w') as file1:
        file1.write(init_input)

def on_connect(client, userdata, flags, rc): 
   debuglog("Connected with result code " + str(rc))    
   client.subscribe("pi/pub_interval") 
   client.publish('pi/pub_interval', interval) 
   debuglog("Published INTERVAL from pub_interval.py")

def on_message(client, userdata, msg):
   if msg.topic == 'pi/pub_interval':
        debuglog("Received INTERVAL in self subscribe")
        debuglog(msg.topic+" "+str( msg.payload))

   init_data = "interval"+" = "+str(interval)
   init_interval_data(init_data)

client = mqtt.Client() 
client.on_connect = on_connect
client.on_message = on_message
client.connect('192.168.1.22', 1883, 60) 
client.loop_start()
debuglog('Script is running, press Ctrl-C to quit...') 
while True:
   time.sleep(2)
   break
   