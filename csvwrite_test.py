# importing the csv module
import csv

# field names
fields = ['Location', 'DateTime', 'Temp', 'Hum', 'Temp', 'Hum']

# data rows of csv file
rows = [['testtime', 'testtemp', 'testhum']]

# name of csv file
filename = "WatSoft_temp_hum.csv"

# writing to csv file
with open(filename, 'w') as csvfile:
	# creating a csv writer object
	csvwriter = csv.writer(csvfile)
	
	# writing the fields
	csvwriter.writerow(fields)
	
	# writing the data rows
	csvwriter.writerows(rows)
