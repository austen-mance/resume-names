import pandas as pd

# drop duplicates

df = pd.DataFrame.from_csv('dataset.csv')
df.drop_duplicates(cols="link")

# setup what will become the 6 new datasets

chicago_sales = pd.DataFrame()
chicago_retail = pd.DataFrame()
boston_sales = pd.DataFrame()
boston_retail = pd.DataFrame()
la_sales = pd.DataFrame()
la_retail = pd.DataFrame()

datasets = {'chicago_sales_dataset.csv': chicago_sales, 'chicago_retail_dataset.csv': chicago_retail, 'boston_sales_dataset.csv': boston_sales, 'boston_retail_dataset.csv': boston_retail, 'la_sales_dataset.csv': la_sales, 'la_retail_dataset.csv': la_retail]

# now we break up our df
# into the 6 datasets by
# location and job type

for row in df:
	link = row.link[0]
	df.link[df.link==link] = link.split('?',1)[0]
	if "sales" in df.title[df.link==link][0].lower():
		if "il" in row["location"][0]:
			chicago_sales.append(row)
		if "ma" in row["location"][0]:
			boston_sales.append(row)
		if "ca" in row["location"][0]:
			la_sales.append(row)
	if "retail" in df.title[df.link==link][0].lower():
		if "il" in row["location"]:
			chicago_retail.append(row)
		if "ma" in row["location"][0]:
			boston_retail.append(row)
		if "ca" in row["location"][0]:
			la_retail.append(row)

# save the files as csv

for data in datasets:
	datasets[data].to_csv(data)
