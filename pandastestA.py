# importing pandas package
import pandas as pd
  
# making data frame from csv file
#data = pd.read_csv("/home/pi/Desktop/home_environ.csv", index_col ="Location")

data = pd.read_csv("/home/pi/Desktop/home_environ.csv")
#position = data.iloc[-1]
label = 'DateTime'  
# retrieving columns by indexing operator
#first = data.loc[["Water Softener", "Kitchen"], ["Humid"]]  
#rowsomping = data.iloc[[1,2,3,4]]  
row = len(data.axes[0]) - 1
#print(rowsomping)
output = data.at[row, label]
print(data.iloc[-1])
print(output)
#data.drop(data.index[:20])
#update_data = data.drop(index=data.index[:3])
 
#print(data.iloc[1])
#data.to_csv('/home/pi/Desktop/home_environ.csv')
