import pandas as pd

# drop duplicates

df = pd.DataFrame.from_csv('dataset.csv')
df.drop_duplicates(subset="link")

# setup what will become the 6 new datasets

chicago_sales = pd.DataFrame()
chicago_retail = pd.DataFrame()
boston_sales = pd.DataFrame()
boston_retail = pd.DataFrame()
la_sales = pd.DataFrame()
la_retail = pd.DataFrame()

datasets = {'chicago_sales_dataset.csv': chicago_sales, 'chicago_retail_dataset.csv': chicago_retail, 'boston_sales_dataset.csv': boston_sales, 'boston_retail_dataset.csv': boston_retail, 'la_sales_dataset.csv': la_sales, 'la_retail_dataset.csv': la_retail}

# now we break up our df
# into the 6 datasets by
# location and job type

sales_df = df[df.type == 'Sales']
retail_df = df[df.link == 'Retail']

chicago_sales =sales_df[sales_df.city == 'Chicago']
boston_sales =sales_df[sales_df.city == 'Boston']
la_sales =sales_df[sales_df.city == 'Los Angeles']
chicago_retail =retail_df[retail_df.city == 'Chicago']
boston_retail =retail_df[retail_df.location.city == 'Boston']
la_retail =retail_df[retail_df.location.city == 'Los Angeles']

# save the files as csv

for data in datasets:
	datasets[data].to_csv(data)
