# importing the csv module
import csv
import time  
import paho.mqtt.client as mqtt
import pandas as pd
import csv
from csv import writer
from datetime import datetime
datetime = datetime.now()
# field names
#fields = ['Cycle_Number', 'DateTime']

# data rows of csv file
rows = [['468', datetime]]

# name of csv file
filename = "WatSoft_cycle_number.dat"

# writing to csv file
with open(filename, 'a') as csvfile:
	# creating a csv writer object
	csvwriter = csv.writer(csvfile)
	
	# writing the fields
	#csvwriter.writerow(fields)
	
	# writing the data rows
	csvwriter.writerows(rows)

