import pandas as pd

# drop duplicates

df = pd.DataFrame.from_csv('dataset.csv', index_col='original_link')
df.drop_duplicates(subset="link")

# setup what will become the 6 new datasets

chicago_sales = pd.DataFrame()
chicago_clerical = pd.DataFrame()
nyc_sales = pd.DataFrame()
nyc_clerical = pd.DataFrame()
la_sales = pd.DataFrame()
la_clerical = pd.DataFrame()

# change links

# df.link = df.link.apply(lambda x: x.split('?',1)[0])

# create zip code lists for LA, boston
# check accounts
# edit resumes

# now we break up our df
# into the 6 datasets by
# location and job type

chicago_sales = df[(df.city == 'Chicago') & (df.type == 'Sales')]
nyc_sales = df[(df.city == 'New York') & (df.type == 'Sales')]
la_sales = df[(df.city == 'Los Angeles') & (df.type == 'Sales')]
chicago_clerical = df[(df.city == 'Chicago') & (df.city == 'Clerical')]
nyc_clerical = df[(df.city == 'New York') & (df.type == 'Clerical')]
la_clerical = df[(df.city == 'Los Angeles') & (df.type == 'Clerical')]

# save the files as csv

datasets = {'chicago_sales_dataset.csv': chicago_sales, 'chicago_clerical_dataset.csv': chicago_clerical, 'nyc_sales_dataset.csv': nyc_sales, 'nyc_clerical_dataset.csv': nyc_clerical, 'la_sales_dataset.csv': la_sales, 'la_clerical_dataset.csv': la_clerical}

for data in datasets.keys():
	datasets[data].to_csv(data)
