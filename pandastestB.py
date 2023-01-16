# importing pandas module 
import pandas as pd
import numpy as np 
# reading csv file from url 

data = pd.read_csv("/home/pi/Desktop/home_environ.csv")
 
# creating position and label variables
position = 2
label = 'Date'
     
# calling .at[] method
output = data.at[position, label]
 
# display
print(output)
#=================================

# creating dataframe using DataFrame constructor
df = pd.DataFrame(data)

# Who scored more points ?
print(df[df.Temp == df.Temp.max()])
print(df[df.Temp == df.Temp.min()])
print(df[df.Humid == df.Humid.max()])
print(df[df.Humid == df.Humid.min()])
#====================================
print("date query section")
start_date = '2022-12-16'
end_date = '2022-12-18'
df2 = df.query('Date >= @start_date and Date <= @end_date')
print(df2)
#==========================
print("last 24 hr min max section")
print(df[df2.Temp == df2.Temp.max()])
print(df[df2.Temp == df2.Temp.min()])
#print(df[df2.Humid == df2.Humid.max()])
#print(df[df.Humid == df.Humid.min()])