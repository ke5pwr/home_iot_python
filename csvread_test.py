# importing csv module
import csv
import csv
import time  
import paho.mqtt.client as mqtt
import pandas as pd
import csv
from csv import writer
from datetime import datetime

# csv file name
filename = "WatSoft_cycle_number.dat"
# initializing the titles and rows list
fields = []
rows = []

# reading csv file
with open(filename, 'r') as csvfile:
	# creating a csv reader object
	csvreader = csv.reader(csvfile)
	
	# extracting field names through first row
	fields = next(csvreader)

	# extracting each data row one by one
	for row in csvreader:
		rows.append(row)

	# get total number of rows
	print("Total no. of rows: %d"%(csvreader.line_num))

# printing the field names
print('Field names are:' + ', '.join(field for field in fields))

# printing first 5 rows
print('\nLast 10 rows are:\n')
for row in rows[-1:(csvreader.line_num)]:
	# parsing each column of a row
	for col in row:
		print("%1s"%col,end=" "),
	print('\n')
