import pandas as pd
import csv

##########################
# initial variable setup #
##########################

# drop duplicates

df = pd.DataFrame.from_csv('dataset.csv', index_col = 'original_link')
df.drop_duplicates(subset="link")

#strings to replace numbers with names, colleges, and addresses

names = pd.DataFrame.from_csv('../accounts-new.csv', index_col = 'email')

f = list(names[names.category == 'rb'].firstname)
l = list(names[names.category == 'rb'].lastname)

rb_names = [x + " " + y for x,y in zip(f,l)]

f = list(names[names.category == 'rw'].firstname)
l = list(names[names.category == 'rw'].lastname)

rw_names = [x + " " + y for x,y in zip(f,l)]

f = list(names[names.category == 'pb'].firstname)
l = list(names[names.category == 'pb'].lastname)

pb_names = [x + " " + y for x,y in zip(f,l)]

f = list(names[names.category == 'pw'].firstname)
l = list(names[names.category == 'pw'].lastname)

pw_names = [x + " " + y for x,y in zip(f,l)]

lax_colleges = open('../bk-data/lax/colleges.txt','r').readlines()
nyc_colleges = open('../bk-data/nyc/colleges.txt','r').readlines()
chi_colleges = open('../bk-data/chicago/colleges.txt','r').readlines()
colleges = {'Los Angeles': lax_colleges, 'New York': nyc_colleges, 'Chicago': chi_colleges}

lax_addresses = open('../bk-data/lax/add-zip.txt','r').readlines()
nyc_addresses = open('../bk-data/nyc/add-zip.txt','r').readlines()
chi_addresses = open('../bk-data/chicago/add-zip.txt','r').readlines()
addresses = {'Los Angeles': lax_addresses, 'New York': nyc_addresses, 'Chicago': chi_addresses}



###########################################################################################################################
# this is the big function that will create each dataset 																  #
# it takes the big dataset and segments by first name because we are no longer randomizing first/last name pairs          #
# it takes variables that are numbers are replaces them with the appropriate strings, particularly colleges and addresses #
# in the end, you will have a dataset where each row is every job each person has to apply to, without logging out        #
# the columns are the information a person needs to edit each resume before applying, like resume number and address      #
###########################################################################################################################

def make_datasets(name_list, type):
	if type == 'rb':
		INDEX = 0
	if type == 'rw':
		INDEX = 1
	if type == 'pb':
		INDEX = 2
	if type == 'pw':
		INDEX = 3
	for name in name_list:

		# first get the appropriate rows for each name
		name_num_str = str(name_list.index(name))
		name_subdf = df[df.firstnames.apply(lambda x: x.replace(',','').strip('[').strip(']').split()[INDEX]).isin([name_num_str])]

		dataset = []


		# then loop over the rows, creating each entry
		# INDEX tells you which index to look at for loops based on type

		for index, row in name_subdf.iterrows():

			data_attributes = {}
			data_attributes['link'] = row.link
			data_attributes['college'] = colleges[row.city][int(row.colleges.replace(',','').strip('[').strip(']').split()[INDEX])]
			data_attributes['address'] = addresses[row.city][int(row.addresses.replace(',','').strip('[').strip(']').split()[INDEX])]
			data_attributes['type'] = row.type
			data_attributes['type'] = row.city
			data_attributes['resume'] = int(row.resumes.replace(',','').strip('[').strip(']').split()[INDEX])

			dataset.append(data_attributes)
		# write the file, and name it
		# the file goes in the mturk folder

		filename = "mturk/" + "_".join(name.split()) + '.csv'
		keys = dataset[0].keys()
		with open(filename, 'wb') as output_file:
		    dict_writer = csv.DictWriter(output_file, keys)
		    dict_writer.writeheader()
		    try:
		    	dict_writer.writerows(dataset)
		    except UnicodeEncodeError:
				pass


###########################
# actual dataset creation #
###########################


for names in zip([rb_names, rw_names, pb_names, pw_names], ["rb", "rw", "pb", "pw"]):
	make_datasets(names[0], names[1])
