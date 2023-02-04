# POWDER MILL HOME IOT
    # Water softener regeneration monitoring
    # Environmental temperature & humdity monitoring

# Hey dudes i just overhauled this with PROFESSIONALE new tech directed by Mr Wesley Powell, extraordinaire!

environment = "prod"

import time  
import paho.mqtt.client as mqtt
import pandas as pd
from csv import writer
from datetime import datetime
import traceback
import logging
import sys
import smtplib
import my_secrets
import init_alert_limits
import init_interval
import json

# DEBUG ERROR HANDLING

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

# GLOBAL VARIABLE INTITIALIZATION

interval = init_interval.interval
tA1 = init_alert_limits.tA1
tA2 = init_alert_limits.tA2
tA3 = init_alert_limits.tA3
skipA1ws = 0
skipA2ws = 0
skipA3ws = 0
skipA1ua = 0
skipA2ua = 0
skipA3ua = 0
skipA1kw = 0
skipA2kw = 0
skipA3kw = 0
ws_temp = ""
ws_humid = ""
upattic_temp = ""
upattic_humid = ""
ws_regen_event1 = ""
ws_regen_event2 = ""
ws_regen_number = 1
ws_cycle_list = []
ws_cycle_time = []

# CONNECT AND SUBSCRIBE/PUBLISH VARIABLES VIA MQTT BROKER

def on_connect(client, userdata, flags, rc): 
   debuglog("Connected with result code " + str(rc)) 
   # Subscribing in on_connect() means that if we lose the connection and 
   # reconnect then subscriptions will be renewed. 
   client.subscribe("pi/ws/switch")
   client.subscribe("pi/temp/ws")
   client.subscribe("pi/humid/ws")
   client.subscribe("pi/temp/kitchen")
   client.subscribe("pi/humid/kitchen")
   client.subscribe("pi/temp/upper_attic")
   client.subscribe("pi/humid/upper_attic") 
   client.subscribe('pi/pub_environ_limits_tA1') 
   client.subscribe('pi/pub_environ_limits_tA2')
   client.subscribe('pi/pub_environ_limits_tA3')
   client.subscribe('pi/pub_alert_reset')
   client.subscribe('pi/pub_cycle_reset')
   client.subscribe("pi/pub_interval")
   client.subscribe("pi/phone_notify")
   client.publish('pi/pub_interval', interval)
   debuglog("on connect pub sub operating")

# NOTIFICATION AND FILE SAVE FUNCTION DEFINITIONS

def debuglog(debug_output):
    with open("/home/pi/home_iot/python_"+environment+"/debug.log", 'a') as file1:
        file1.write(str(datetime.now())+" \t"+debug_output+" \n")

def notify_gmail(alert_msg):
    sender_email_id = my_secrets.sender_email_id
    sender_app_password = my_secrets.sender_app_password
    receiver_email_id = my_secrets.receiver_email_id
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender_email_id, sender_app_password)
    s.sendmail(sender_email_id, receiver_email_id, alert_msg)
    debuglog("Gmail notification was published")
    s.quit()

def notify_phone(alert_msg):
    client.publish('pi/phone_notify', alert_msg)
    debuglog("Phone notification was published")

def csvsave(save_filename, save_content):  
    with open(save_filename, 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(save_content)
        f_object.close()

def json_save_environ(ws_temp, ws_humid, upattic_temp, upattic_humid):    
    dictionary ={
        "water_softener_temperature": ws_temp,
        "water_softener_humidity": ws_humid,
        "attic_temperature": upattic_temp,
        "attic_humidity": upattic_humid
    }
    filename = "/var/www/html/home_iot_"+environment+"/environ.json"
    with open(filename, "w") as outfile:
        json.dump(dictionary, outfile)

def json_save_ws_regen(ws_regen_number, ws_regen_event1, ws_regen_event2):    
    dictionary ={
       "ws_regen_number": ws_regen_number, "ws_regen_event1": ws_regen_event1, "ws_regen_event2": ws_regen_event2
    }
    filename = "/var/www/html/home_iot_"+environment+"/ws_regen_event.json"
    with open(filename, "w") as outfile:
        json.dump(dictionary, outfile)

def json_file_variable_import():
    global ws_regen_number
    filename = "/var/www/html/home_iot_"+environment+"/ws_regen_event.json"
    if filename:
        with open(filename, 'r') as f:
            datastore = json.load(f)    
    ws_regen_number = datastore["ws_regen_number"]
    debuglog("ws_regen_number = "+str(ws_regen_number))
    ws_regen_number = int(datastore["ws_regen_number"]) +1
    debuglog("ws_regen_number = "+str(ws_regen_number))

# MAIN LOOP TO EXECUTE WHEN MESSAGES RECEIVED

def on_message(client, userdata, msg):
    if msg.topic == 'pi/ws/switch':
        on_message_cycle_ws(client, userdata, msg) 
    elif msg.topic == 'pi/pub_cycle_reset':
        on_message_cycle_reset(client, userdata, msg)
    elif msg.topic == 'pi/pub_interval':
        on_message_pub_interval(client, userdata, msg)
    else:
        on_message_environ(client, userdata, msg)

# RESET CYCLE LIST AFTER REGENERATION.  
# SEPARATE SCRIPT RUNS DAILY AT NOON VIA CRONTAB TO TRIGGER THIS FUNCTION.

def on_message_cycle_reset(client, userdata, msg):
    if msg.topic == 'pi/pub_cycle_reset':
        save_content = msg.topic+" "+str( msg.payload) 
        debuglog(save_content)
        ws_cycle_list.clear()
        ws_cycle_time.clear()
        debuglog(str(ws_cycle_list))
        debuglog(str(ws_cycle_time))

# SETS PUBLISH INTERVAL ON ARDUINOS FOR ENVIRONMENTAL SENSORS.
# RUNS UPON SCRIPT STARTUP AND ON DEMAND FROM SEPARATE SCRIPT

def on_message_pub_interval(client, userdata, msg):
    if msg.topic == 'pi/pub_interval':
        save_content = msg.topic+" "+str( msg.payload) 
        debuglog(save_content)
        
# RUNS ENVIRONMENTAL MONITORING, RECORDING, AND ALERTS

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
    global tA1
    global tA2
    global tA3

# alerts ping once and then skipped to avoid multiple pings.  this if statement resets the alerts.
    if msg.topic == 'pi/pub_alert_reset':
        skipA1ws = 0
        skipA2ws = 0
        skipA3ws = 0
        skipA1ua = 0
        skipA2ua = 0
        skipA3ua = 0
        skipA1kw = 0
        skipA2kw = 0
        skipA3kw = 0
        debuglog("Environmental alerts reset")

# separate script sets alert levels on demand.  this if statement sets the limits in main script.
    if msg.topic == 'pi/pub_environ_limits_tA1':
        tA1 = int(msg.payload.decode("utf-8"))
        debuglog(msg.payload.decode("utf-8"))
    
    if msg.topic == 'pi/pub_environ_limits_tA2':
        tA2 = int(msg.payload.decode("utf-8"))
        debuglog(msg.payload.decode("utf-8"))

    if msg.topic == 'pi/pub_environ_limits_tA3':
        tA3 = int(msg.payload.decode("utf-8"))
        debuglog(msg.payload.decode("utf-8"))

    if msg.topic == 'pi/temp/ws':
        location = "Water Softener"
        environ_temp = msg.payload.decode("utf-8")
        environ_humid = ""
        global ws_temp
        global ws_humid
        global upattic_temp
        global upattic_humid

        ws_temp = environ_temp
        json_save_environ(ws_temp, ws_humid, upattic_temp, upattic_humid)

        if float(environ_temp) < tA1 and float(environ_temp) >= tA2 and skipA1ws == 0:
            alert_msg = location+" temp below "+str(tA1)+"F"
            debuglog(alert_msg)
            notify_gmail(alert_msg)
            notify_phone(alert_msg)
            skipA1ws = 1
        elif float(environ_temp) < tA2 and float(environ_temp) >= tA3 and skipA2ws == 0:
            alert_msg = location+" temp below "+str(tA2)+"F"
            debuglog(alert_msg)
            notify_gmail(alert_msg)   
            notify_phone(alert_msg)     
            skipA2ws = 1
        elif float(environ_temp) < tA3 and float(environ_temp) >= 0 and skipA3ws == 0:
            alert_msg = location+" temp below "+str(tA3)+"F"
            debuglog(alert_msg)
            notify_gmail(alert_msg)
            notify_phone(alert_msg)
            skipA3ws = 1

    elif msg.topic == 'pi/humid/ws':
        location = "Water Softener"
        environ_temp = ""
        environ_humid = msg.payload.decode("utf-8")
        ws_humid = environ_humid
        
        ws_humid = environ_humid
        json_save_environ(ws_temp, ws_humid, upattic_temp, upattic_humid)

    elif msg.topic == 'pi/temp/kitchen':
        location = "Kitchen"
        environ_temp = msg.payload.decode("utf-8")
        environ_humid = ""

        if float(environ_temp) < tA1 and float(environ_temp) >= tA2 and skipA1kw == 0:
            alert_msg = location+" temp below "+str(tA1)+"F"
            debuglog(alert_msg)
            notify_gmail(alert_msg)
            notify_phone(alert_msg)
            skipA1kw = 1
        elif float(environ_temp) < tA2 and float(environ_temp) >= tA3 and skipA2kw == 0:
            alert_msg = location+" temp below "+str(tA2)+"F"
            debuglog(alert_msg)
            notify_gmail(alert_msg)          
            notify_phone(alert_msg)
            skipA2kw = 1
        elif float(environ_temp) < tA3 and float(environ_temp) >= 0 and skipA3kw == 0:
            alert_msg = location+" temp below "+str(tA3)+"F"
            debuglog(alert_msg)
            notify_gmail(alert_msg)
            notify_phone(alert_msg)
            skipA3kw = 1

    elif msg.topic == 'pi/humid/kitchen':
        location = "Kitchen"
        environ_temp = ""
        environ_humid = msg.payload.decode("utf-8")

    elif msg.topic == 'pi/temp/upper_attic':
        location = "Upper attic"
        environ_temp = msg.payload.decode("utf-8")
        environ_humid = ""
        upattic_temp = environ_temp

        upattic_temp = environ_temp
        json_save_environ(ws_temp, ws_humid, upattic_temp, upattic_humid)

        if float(environ_temp) < tA1 and float(environ_temp) >= tA2 and skipA1ua == 0:
            alert_msg = location+" temp below "+str(tA1)+"F"
            debuglog(alert_msg)
            notify_gmail(alert_msg)
            notify_phone(alert_msg)
            skipA1ua = 1
        elif float(environ_temp) < tA2 and float(environ_temp) >= tA3 and skipA2ua == 0:
            alert_msg = location+" temp below "+str(tA2)+"F"
            debuglog(alert_msg)
            notify_gmail(alert_msg)  
            notify_phone(alert_msg)        
            skipA2ua = 1
        elif float(environ_temp) < tA3 and float(environ_temp) >= 0 and skipA3ua == 0:
            alert_msg = location+" temp below "+str(tA3)+"F"
            debuglog(alert_msg)
            notify_gmail(alert_msg)
            notify_phone(alert_msg)
            skipA3ua = 1

    elif msg.topic == 'pi/humid/upper_attic':
        location = "Upper attic"
        environ_temp = ""
        environ_humid = msg.payload.decode("utf-8")
        upattic_humid = environ_humid

        upattic_humid = environ_humid
        json_save_environ(ws_temp, ws_humid, upattic_temp, upattic_humid)

    else:
         return    
        
    environ_time = datetime.now()
    environ_date = environ_time.strftime("%-Y-%m-%d")
    environ_time = environ_time.strftime("%I:%M:%S %p")
    save_filename = "/home/pi/home_iot/python_"+environment+"/home_environ.csv"   
    environ_list = [location, environ_date, environ_time, environ_temp, environ_humid]
    csvsave(save_filename, environ_list)

# THIS FUNCTION MONITORS, RECORDS, ALERTS WATER SOFTENER REGENERATION CYCLE OPERATION

def on_message_cycle_ws(client, userdata, msg): 
   global ws_regen_number 
   global ws_regen_event1
   global ws_regen_event2 

# separate script sends test signals to mimic water softerer regeneration switches
   if msg.topic == 'pi/ws/switch' and msg.payload == b'TEST':
        ws_cycle_csv = ["\n*************  THIS IS A TEST FROM ws_cycle_publish_test.py   *************"]
        debuglog(str(ws_cycle_csv))
        debuglog(msg.topic+" "+str( msg.payload))
        save_filename = "/home/pi/home_iot/python_"+environment+"/ws_cycle.csv"
        csvsave(save_filename, ws_cycle_csv) 

   if msg.topic == 'pi/ws/switch' and msg.payload == b'SWITCH':
       ws_cycle_list.append (1)
       save_filename = "/home/pi/home_iot/python_"+environment+"/ws_cycle.csv"

# decode and report out each stage of the regen cycle   
   if len(ws_cycle_list) == 1:
       bw_start = datetime.now()
       ws_cycle_time.append (bw_start)
       cycle_status = "Cycle start"
       alert_msg = "Watersoftener regen started"
      
       ws_cycle_csv = ["\n**********************\n"+cycle_status, bw_start,]
       csvsave(save_filename, ws_cycle_csv)
       debuglog(cycle_status+"         "+str(bw_start))   
       debuglog("Switch1")          
       notify_gmail(alert_msg)
       notify_phone(alert_msg)

       json_file_variable_import()     
       debuglog(str(ws_regen_number))
       ws_regen_event1 = (str(bw_start))
       ws_regen_event2 = ""
       json_save_ws_regen(ws_regen_number, ws_regen_event1, ws_regen_event2)     

   elif len(ws_cycle_list) == 2:
       debuglog("Switch2")
       
   elif len(ws_cycle_list) == 3:
       debuglog("Switch3")

   elif len(ws_cycle_list) == 4:
       rinse_start = datetime.now()
       ws_cycle_time.append (rinse_start)
       cycle_status = "Backwash"
       bw_duration = rinse_start - ws_cycle_time[0]
       ws_cycle_csv = [cycle_status, "", bw_duration]
       csvsave(save_filename, ws_cycle_csv)
       debuglog(cycle_status+"         "+str(bw_duration))
       debuglog("Switch4")
            
   elif len(ws_cycle_list) == 5:
       fill_start = datetime.now()
       ws_cycle_time.append (fill_start)
       cycle_status = "Rinse"
       rinse_duration = fill_start - ws_cycle_time[1]
       ws_cycle_csv = [cycle_status, "", rinse_duration]
       csvsave(save_filename, ws_cycle_csv)
       debuglog(cycle_status+"         "+str(rinse_duration))
       debuglog("Switch5")

   elif len(ws_cycle_list) == 6:
       debuglog("Switch6") 

   elif len(ws_cycle_list) == 7:
       brine_start = datetime.now()
       ws_cycle_time.append (brine_start)
       cycle_status = "Fill"
       fill_duration = brine_start - ws_cycle_time[2]
       ws_cycle_csv = [cycle_status, "", fill_duration]
       csvsave(save_filename, ws_cycle_csv)
       debuglog(cycle_status+"             "+str(fill_duration))
       debuglog("Switch7")
            
   elif len(ws_cycle_list) == 8:
       bw2_start = datetime.now()
       ws_cycle_time.append (bw2_start)
       cycle_status = "Brine"
       brine_duration = bw2_start - ws_cycle_time[3]
       ws_cycle_csv = [cycle_status, "", brine_duration]
       csvsave(save_filename, ws_cycle_csv)
       debuglog(cycle_status+"            "+str(brine_duration))
       debuglog("Switch8")

   elif len(ws_cycle_list) == 9:
       rinse_start = datetime.now()
       ws_cycle_time.append (rinse_start)
       cycle_status = "Backwash"
       bw2_duration = rinse_start - ws_cycle_time[4]                  
       ws_cycle_csv = [cycle_status, "", bw2_duration]
       csvsave(save_filename, ws_cycle_csv)
       debuglog(cycle_status+"         "+str(bw2_duration))  
       debuglog("Switch9")

   elif len(ws_cycle_list) == 10:                   
       serv_start = datetime.now()
       ws_cycle_time.append (serv_start)
       cycle_status = "Rinse"
       rinse_duration = serv_start - ws_cycle_time[5]           
       cycle_duration = ws_cycle_time[6] - ws_cycle_time[0]
       ws_cycle_csv = [cycle_status,"", rinse_duration]
       csvsave(save_filename, ws_cycle_csv)
       debuglog(cycle_status+"   "+str(rinse_duration))   
       debuglog("Switch10")
       debuglog("Cycle duration"+"   "+str(cycle_duration))
       debuglog("Cycle complete"+"   "+str(ws_cycle_time[6]))
       debuglog(str(ws_cycle_time[6]))    
       ws_cycle_csv = ["Cycle complete", serv_start, cycle_duration]
       csvsave(save_filename, ws_cycle_csv)
            

       ws_regen_event2 = (str(serv_start))
       json_save_ws_regen(ws_regen_number, ws_regen_event1, ws_regen_event2)  

       alert_msg = "Watersoftener regen completed"
       notify_gmail(alert_msg)
       notify_phone(alert_msg)
                   
   elif len(ws_cycle_list) > 10:
       error = datetime.now()
       ws_cycle_time.append (len(ws_cycle_list))
       error_duration = error - ws_cycle_time[5]
       debuglog("UNEXPECTED STATE")
       debuglog("  len(ws_cycle_list)    {}".format(len(ws_cycle_list)))
       debuglog("  time:        {}".format(ws_cycle_time))
       debuglog("  msg.topic    {}".format(msg.topic))
       debuglog("  msg.payload  {}".format(msg.payload))
  
       ws_cycle_csv = ["Error", len(ws_cycle_list), error_duration]
       csvsave(save_filename, ws_cycle_csv)

       alert_msg = "Regen exceeded expected number of stages!"
       notify_gmail(alert_msg)
       notify_phone(alert_msg)

# THIS IS THE MAIN LOOP TO CONNECT MQTT BROKER ON RPi, AND PUBLISH AND SUBSCRIBE SIGNALS.

try:
    client = mqtt.Client() 
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('192.168.1.22', 1883, 60) 
    
    client.loop_start() 
    while True:
        time.sleep(2)
        pass
               
except Exception as e:
        logging.error("Main thread exception")
        logging.error(traceback.format_exc())