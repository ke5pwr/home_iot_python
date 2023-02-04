environment = "prod"

import time  
import paho.mqtt.client as mqtt
from datetime import datetime

tA1 = 35
tA2 = 33
tA3 = 32
reset = 1

def debuglog(debug_output):
    with open("/home/pi/home_iot/python_"+environment+"/debug.log", 'a') as file1:
        file1.write(str(datetime.now())+" \t"+debug_output+" \n")

def init_alert_limits_data(init_input):
    with open("/home/pi/home_iot/python_"+environment+"/init_alert_limits.py", 'w') as file1:
        file1.write(init_input)

def on_connect(client, userdata, flags, rc): 
   debuglog("Connected with result code " + str(rc))    
   client.subscribe('pi/pub_environ_limits_tA1')
   client.subscribe('pi/pub_environ_limits_tA2')
   client.subscribe('pi/pub_environ_limits_tA3')
   client.publish('pi/pub_alert_reset', reset)
   client.publish('pi/pub_environ_limits_tA1', tA1)
   client.publish('pi/pub_environ_limits_tA2', tA2)
   client.publish('pi/pub_environ_limits_tA3', tA3)
   debuglog("Environmental limits PUBLISHED")

def on_message(client, userdata, msg):
   debuglog("Environmental limits self subscribed")

   limits = "tA1"+" = "+str(tA1)+"\n"+"tA2"+" = "+str(tA2)+"\n"+"tA3"+" = "+str(tA3)
   init_alert_limits_data(limits)


   if msg.topic == 'pi/pub_environ_limits_tA1':
        debuglog(msg.topic+" "+str( msg.payload))

   if msg.topic == 'pi/pub_environ_limits_tA2':
        debuglog(msg.topic+" "+str( msg.payload))

   if msg.topic == 'pi/pub_environ_limits_tA3':
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
   