# RPi

import time  
import paho.mqtt.client as mqtt
import pandas as pd
import csv
from csv import writer
from datetime import datetime
from pushbullet import PushBullet
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
import traceback
import logging
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

interval = 60 
tA1 = 35
tA2 = 33
tA3 = 32
skipA1ws = 0
skipA2ws = 0
skipA3ws = 0
skipA1ua = 0
skipA2ua = 0
skipA3ua = 0
skipA1kw = 0
skipA2kw = 0
skipA3kw = 0
# hey bro dude i just added this new tech w sir wesley powell
access_token = "PUT TOKEN HERE"
data = "Home Alert!"

# Setup callback functions that are called when MQTT events happen like 
# connecting to the server or receiving data from a subscribed feed. 
def on_connect(client, userdata, flags, rc): 
   print("Connected with result code " + str(rc)) 
   # Subscribing in on_connect() means that if we lose the connection and 
   # reconnect then subscriptions will be renewed. 
   print("got this far1")
   client.subscribe("pi/ws/switch")
   client.subscribe("pi/temp/ws")
   client.subscribe("pi/humid/ws")
   client.subscribe("pi/temp/kitchen")
   client.subscribe("pi/humid/kitchen")
   client.subscribe("pi/temp/upper_attic")
   client.subscribe("pi/humid/upper_attic")  
   print("got this far2")
   client.subscribe("pi/pub_interval")
   client.publish('pi/pub_interval', interval)
   print("got this far3")
#   client.subscribe("pi/leds/pi")
# Create a list to count the switch on off iterations for the Operations Monitoring Section, and list to store cycle stage times
ws_cycle_list = []
ws_cycle_time = []

# ENVIRONMENTAL MONITORING SECTION

# The callback for when a PUBLISH message is received from the server. 

def notify(text):
    pb = PushBullet(access_token)
    push = pb.push_note(data, text)
    put_success("Message sent successfully...")
    time.sleep(3)
    clear()
    clear()
        
def on_message(client, userdata, msg):
    if msg.topic == 'pi/ws/switch':
        on_message_cycle_ws(client, userdata, msg)       
    elif msg.topic == 'pi/pub_interval':
        on_message_pub_interval(client, userdata, msg)
    else:
        on_message_environ(client, userdata, msg)

def on_message_pub_interval(client, userdata, msg):
    if msg.topic == 'pi/pub_interval':
        print("gotit")
        print(msg.topic+" "+str( msg.payload))   
       
def on_message_environ(client, userdata, msg):
    global skipA1ws
    global skipA2ws
    global skipA3ws
    global skipA1ua
    global skipA2ua
    global skipA3ua
    global skipA1kw
    global skipA2kw
    global skipA3kw
    
    if msg.topic == 'pi/temp/ws':
        location = "Water Softener"
        environ_temp = msg.payload.decode("utf-8")
        environ_humid = ""

        if float(environ_temp) < tA1 and float(environ_temp) >= tA2 and skipA1ws == 0:
            alert_msg = location+" temp below "+str(tA1)+"F"
            print(alert_msg)
            notify(alert_msg)
            skipA1ws = 1
        elif float(environ_temp) < tA2 and float(environ_temp) >= tA3 and skipA2ws == 0:
            alert_msg = location+" temp below "+str(tA2)+"F"
            print(alert_msg)
            notify(alert_msg)          
            skipA2ws = 1
        elif float(environ_temp) < tA3 and float(environ_temp) >= 0 and skipA3ws == 0:
            alert_msg = location+" temp below "+str(tA3)+"F"
            print(alert_msg)
            notify(alert_msg)
            skipA3ws = 1

    elif msg.topic == 'pi/humid/ws':
        location = "Water Softener"
        environ_temp = ""
        environ_humid = msg.payload.decode("utf-8")

    elif msg.topic == 'pi/temp/kitchen':
        location = "Kitchen"
        environ_temp = msg.payload.decode("utf-8")
        environ_humid = ""

        if float(environ_temp) < tA1 and float(environ_temp) >= tA2 and skipA1kw == 0:
            alert_msg = location+" temp below "+str(tA1)+"F"
            print(alert_msg)
            notify(alert_msg)
            skipA1kw = 1
        elif float(environ_temp) < tA2 and float(environ_temp) >= tA3 and skipA2kw == 0:
            alert_msg = location+" temp below "+str(tA2)+"F"
            print(alert_msg)
            notify(alert_msg)          
            skipA2kw = 1
        elif float(environ_temp) < tA3 and float(environ_temp) >= 0 and skipA3kw == 0:
            alert_msg = location+" temp below "+str(tA3)+"F"
            print(alert_msg)
            notify(alert_msg)
            skipA3kw = 1

    elif msg.topic == 'pi/humid/kitchen':
        location = "Kitchen"
        environ_temp = ""
        environ_humid = msg.payload.decode("utf-8")

    elif msg.topic == 'pi/temp/upper_attic':
        location = "Upper attic"
        environ_temp = msg.payload.decode("utf-8")
        environ_humid = ""

        if float(environ_temp) < tA1 and float(environ_temp) >= tA2 and skipA1ua == 0:
            alert_msg = location+" temp below "+str(tA1)+"F"
            print(alert_msg)
            notify(alert_msg)
            skipA1ua = 1
        elif float(environ_temp) < tA2 and float(environ_temp) >= tA3 and skipA2ua == 0:
            alert_msg = location+" temp below "+str(tA2)+"F"
            print(alert_msg)
            notify(alert_msg)          
            skipA2ua = 1
        elif float(environ_temp) < tA3 and float(environ_temp) >= 0 and skipA3ua == 0:
            alert_msg = location+" temp below "+str(tA3)+"F"
            print(alert_msg)
            notify(alert_msg)
            skipA3ua = 1

    elif msg.topic == 'pi/humid/upper_attic':
        location = "Upper attic"
        environ_temp = ""
        environ_humid = msg.payload.decode("utf-8")
        
    environ_time = datetime.now()
    environ_date = environ_time.strftime("%-Y-%m-%d")
    environ_time = environ_time.strftime("%I:%M:%S %p")
    print(location+" "+environ_temp+"  "+environ_humid+"  "+str(environ_date+"   "+str(environ_time)))
              
    environ_list = [location, environ_date, environ_time, environ_temp, environ_humid]
    with open('/home/pi/Desktop/home_environ.csv', 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(environ_list)
        f_object.close()       


# CYCLE OPERATION MONITORING SECTION

def on_message_cycle_ws(client, userdata, msg): 
   if msg.topic == 'pi/ws/switch' and msg.payload == b'SWITCH':
       ws_cycle_list.append (1)

# Append one item to list each iteration -- where's the good old fortran goto when you need it   
       
# Decode and report out each stage of the regen cycle
   
   
   if len(ws_cycle_list) == 1:
       bw_start = datetime.now()
       ws_cycle_time.append (bw_start)
       print('\n')
       print("Cycle start"+"      "+str(bw_start))
       
       ws_cycle_csv = ["\n"]
       with open('/home/pi/Desktop/WatSoft_cycle.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(ws_cycle_csv)
            f_object.close()
            
       ws_cycle_csv = ["Cycle start", bw_start, ""]
       with open('/home/pi/Desktop/WatSoft_cycle.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(ws_cycle_csv)
            f_object.close()
            
            alert_msg = "Cycle started "+str(ws_cycle_time[0])
            notify(alert_msg)
            
   elif len(ws_cycle_list) == 2:
       print("Switch2")
       
   elif len(ws_cycle_list) == 3:
       print("Switch3")

   elif len(ws_cycle_list) == 4:
       rinse_start = datetime.now()
       ws_cycle_time.append (rinse_start)
       bw_duration = rinse_start - ws_cycle_time[0]
       print("Backwash"+"         "+str(bw_duration))
       
       ws_cycle_csv = ["Backwash", "", bw_duration]
       with open('/home/pi/Desktop/WatSoft_cycle.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(ws_cycle_csv)
            f_object.close()
            
   elif len(ws_cycle_list) == 5:
       print("test5")
       fill_start = datetime.now()
       ws_cycle_time.append (fill_start)
       rinse_duration = fill_start - ws_cycle_time[1]
       print("Rinse"+"         "+str(rinse_duration))
       
       ws_cycle_csv = ["Rinse", "", rinse_duration]
       with open('/home/pi/Desktop/WatSoft_cycle.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(ws_cycle_csv)
            f_object.close()
 
   elif len(ws_cycle_list) == 6:
       print("Switch6") 

   elif len(ws_cycle_list) == 7:
       print("test7")
       brine_start = datetime.now()
       ws_cycle_time.append (brine_start)
       fill_duration = brine_start - ws_cycle_time[2]
       print("Fill"+"             "+str(fill_duration))
       
       ws_cycle_csv = ["Fill", "", fill_duration]
       with open('/home/pi/Desktop/WatSoft_cycle.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(ws_cycle_csv)
            f_object.close()
            
   elif len(ws_cycle_list) == 8:
       print("test8")
       bw2_start = datetime.now()
       ws_cycle_time.append (bw2_start)
       brine_duration = bw2_start - ws_cycle_time[3]
       print("Brine"+"            "+str(brine_duration))

       ws_cycle_csv = ["Brine", "", brine_duration]
       with open('/home/pi/Desktop/WatSoft_cycle.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(ws_cycle_csv)
            f_object.close()

   elif len(ws_cycle_list) == 9:
       print("test9")
       rinse_start = datetime.now()
       ws_cycle_time.append (rinse_start)
       bw2_duration = rinse_start - ws_cycle_time[4]
       print("Backwash"+"         "+str(bw2_duration))            

       ws_cycle_csv = ["Backwash", "", bw2_duration]
       with open('/home/pi/Desktop/WatSoft_cycle.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(ws_cycle_csv)
            f_object.close()
            
   elif len(ws_cycle_list) == 10:                   
       print("test10")
       serv_start = datetime.now()
       ws_cycle_time.append (serv_start)
       rinse_duration = serv_start - ws_cycle_time[5]           
       cycle_duration = ws_cycle_time[6] - ws_cycle_time[0]
       print("Rinse duration"+"   "+str(rinse_duration))     
       print("Cycle duration"+"   "+str(cycle_duration))
       print("Cycle complete"+"   "+str(ws_cycle_time[6]))
       print(ws_cycle_time[6])
       
       # hello again
       ws_cycle_csv = ["Rinse","", rinse_duration]
       with open('/home/pi/Desktop/WatSoft_cycle.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(ws_cycle_csv)
            f_object.close()
            
       ws_cycle_csv = ["Cycle complete", serv_start, cycle_duration]
       with open('/home/pi/Desktop/WatSoft_cycle.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(ws_cycle_csv)
            f_object.close()
            
            alert_msg = "Cycle complete "+str(ws_cycle_time[6])
            notify(alert_msg)
                   
   elif len(ws_cycle_list) > 10:
       error = datetime.now()
       ws_cycle_time.append (len(ws_cycle_list))
       error_duration = error - ws_cycle_time[5]
       print("UNEXPECTED STATE")
       print("  len(ws_cycle_list)    {}".format(len(ws_cycle_list)))
       print("  time:        {}".format(ws_cycle_time))
       print("  msg.topic    {}".format(msg.topic))
       print("  msg.payload  {}".format(msg.payload))
  
       ws_cycle_csv = ["Error", len(ws_cycle_list), error_duration]
       with open('/home/pi/Desktop/WatSoft_cycle.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(ws_cycle_csv)
            f_object.close()

            alert_msg = "Regen exceeded program stages "+str(ws_cycle_time[6])
            notify(alert_msg)

# Create MQTT client and connect to localhost, i.e. the Raspberry Pi running 
# this script and the MQTT server. 
try:
    client = mqtt.Client() 
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('192.168.1.22', 1883, 60) 
# Connect to the MQTT server and process messages in a background thread. 

    # hello from git
    client.loop_forever() 
# Main loop to listen for button presses. 
    print('Script is running, press Ctrl-C to quit...') 

except Exception as e:
        logging.error("Main thread exception")
        logging.error(traceback.format_exc())
