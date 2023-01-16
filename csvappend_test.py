# Import writer class from csv module
from csv import writer
somping = "wowser"
# List that we want to add as a new row
List = [6, 'William', 5532, somping]

# Open our existing CSV file in append mode
# Create a file object for this file
with open('WatSoft_temp_hum.csv', 'a') as f_object:

	# Pass this file object to csv.writer()
	# and get a writer object
	writer_object = writer(f_object)

	# Pass the list as an argument into
	# the writerow()
	writer_object.writerow(List)

	# Close the file object
	f_object.close()
