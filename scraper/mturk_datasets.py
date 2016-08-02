import pandas as pd
import csv
import time
import sys
import random
import datetime
import re
import os
from random import sample

from docx import Document
from selenium import webdriver

##########################
# initial variable setup #
##########################

# drop duplicates

df = pd.DataFrame.from_csv('dataset.csv', index_col = 'original_link')
df.drop_duplicates(subset="link")
num_jobs = len(df)

#strings to replace numbers with names, colleges, and addresses

names = pd.DataFrame.from_csv('../accounts-new.csv').reset_index()

f = list(names[names.category == 'rb'].firstname)
l = list(names[names.category == 'rb'].lastname)

rb_names = [x + " " + y for x,y in zip(f,l)]
rb_emails = list(names[names.category == 'rb'].email)
rb = [rb_names, rb_emails]

f = list(names[names.category == 'rw'].firstname)
l = list(names[names.category == 'rw'].lastname)

rw_names = [x + " " + y for x,y in zip(f,l)]
rw_emails = list(names[names.category == 'rw'].email)
rw = [rw_names, rw_emails]

f = list(names[names.category == 'pb'].firstname)
l = list(names[names.category == 'pb'].lastname)

pb_names = [x + " " + y for x,y in zip(f,l)]
pb_email = list(names[names.category == 'pb'].email)
pb = [pb_names, pb_email]

f = list(names[names.category == 'pw'].firstname)
l = list(names[names.category == 'pw'].lastname)

pw_names = [x + " " + y for x,y in zip(f,l)]
pw_emails = list(names[names.category == 'pw'].email)
pw = [pw_names, pw_emails]

lax_colleges = open('../bk-data/lax/colleges.txt','r').readlines()
nyc_colleges = open('../bk-data/nyc/colleges.txt','r').readlines()
chi_colleges = open('../bk-data/chicago/colleges.txt','r').readlines()
colleges = {'Los Angeles': lax_colleges, 'New York': nyc_colleges, 'Chicago': chi_colleges}

lax_addresses = open('../bk-data/lax/add-zip.txt','r').readlines()
nyc_addresses = open('../bk-data/nyc/add-zip.txt','r').readlines()
chi_addresses = open('../bk-data/chicago/add-zip.txt','r').readlines()
addresses = {'Los Angeles': lax_addresses, 'New York': nyc_addresses, 'Chicago': chi_addresses}

big_dataset = []

# progress bar function

def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()

###########################################################################################################################
# this is the big function that will create each dataset 																  #
# it takes the big dataset and segments by first name because we are no longer randomizing first/last name pairs          #
# it takes variables that are numbers are replaces them with the appropriate strings, particularly colleges and addresses #
# in the end, you will have a dataset where each row is every job each person has to apply to, without logging out        #
# the columns are the information a person needs to edit each resume before applying, like resume number and address      #
# there are also a few helper functions to avoid hairballing 															  #
###########################################################################################################################

# creates data for CSV creation, also used later for making resumes

def make_data(row, INDEX, index, email_list, name_list, name):
	data_attributes = {}
	data_attributes['link'] = row.link
	data_attributes['college'] = colleges[row.city][int(row.colleges.replace(',','').strip('[').strip(']').split()[INDEX])]
	data_attributes['address'] = addresses[row.city][int(row.addresses.replace(',','').strip('[').strip(']').split()[INDEX])]
	data_attributes['job_type'] = row.type
	data_attributes['city'] = row.city
	data_attributes['resume_type'] = int(row.resumes.replace(',','').strip('[').strip(']').split()[INDEX])
	data_attributes['resume'] = index
	data_attributes['email'] = email_list[name_list.index(name)]
	data_attributes['password'] = 'evanis#1'
	return data_attributes

# does actual text editing

def make_resume(data_attributes, file_name):

	resume = str(data_attributes['resume_type']) + '.docx'
	document = Document("../" + data_attributes['job_type'] + "/" + resume)

	# replaces info as needed

	for paragraph in document.paragraphs:
		if '{NAME}' in paragraph.text:
			paragraph.text = data_attributes['name']
		if '{EMAILADDRESS}' in paragraph.text:
			paragraph.text = 'Email: ' + data_attributes['email']
		if '{MAILADDRESS}' in paragraph.text:
			paragraph.text = data_attributes['address']
		if '{UNIVERSITY}' in paragraph.text:
			paragraph.text = data_attributes['college']
	document.save('mturk/' + data_attributes['name'] + '/' + file_name + '_resume_' + str(data_attributes['resume']) + '.docx')

# a helper function for text

elapsed = lambda time, start_time: str(int((time - start_time)/60)) + " minutes and " + str((time - start_time)%60) + " seconds"

def make_datasets(lists, type, start_time, count):

	print "#####################"
	print "#Starting on type " + type + '#'
	print "#####################"

	# variable initialization

	name_list = lists[0]
	email_list = lists[1]
	if type == 'rb':
		INDEX = 0
	if type == 'rw':
		INDEX = 1
	if type == 'pb':
		INDEX = 2
	if type == 'pw':
		INDEX = 3

	for name in name_list:

		# housekeeping, prints progress in terminal, starts time counter, and creates file path if none exists to avoid errors
		print "Working on " + name

		time_begin = time.time()

		if not os.path.exists('mturk/' + name):
			os.makedirs('mturk/' + name)

		file_name = "_".join(name.split())

		# first get the appropriate rows for each name
		# these are rows that each "person" is supposed to apply to

		name_num_str = str(name_list.index(name))
		name_subdf = df[df.firstnames.apply(lambda x: x.replace(',','').strip('[').strip(']').split()[INDEX]).isin([name_num_str])].reset_index()
		num_jobs = len(name_subdf)
		i = 0
		dataset = []


		# then loop over the rows, creating each entry
		# INDEX tells you which index to look at for loops based on type

		for index, row in name_subdf.iterrows():

			# make datasets and add them to the big datasets

			data_attributes = make_data(row, INDEX, index, email_list, name_list, name)
			dataset.append(data_attributes)
			data_attributes['name'] = name
			big_dataset.append(data_attributes)

			#create resume

			make_resume(data_attributes, file_name)

			# housekeeping for terminal

			i += 1
			count += 1
			progress(i, num_jobs)
		
		# write the file, and name it
		# the file goes in the mturk folder
		# CSVs have their own folder for easy access

		print "Writing final CSV for " + name

		if not os.path.exists('mturk/CSVs'):
			os.makedirs('mturk/CSVs')

		filename = "mturk/CSVs/" + file_name + '.csv'
		keys = dataset[0].keys()
		with open(filename, 'wb') as output_file:
		    dict_writer = csv.DictWriter(output_file, keys)
		    dict_writer.writeheader()
		    try:
		    	dict_writer.writerows(dataset)
		    except UnicodeEncodeError:
				pass

		# some progress stuff for the terminal

		print str(9 - name_list.index(name)) + " left for type " + type
		print "Time spent: " + elapsed(time.time(), time_begin)
		print "Time elapsed: " + elapsed(time.time(), start_time)
		frac_done = float(count/num_jobs)
		print "Approximately " + elapsed(frac_done*1200, 0) + " remaining, current progress: " + str(frac_done) + "%"

	print "Ending type " + type + ", current progress: " + str(frac_done)


###########################
# actual dataset creation #
###########################

start_time = time.time()
count = 0
for names in zip([rb, rw, pb, pw], ["rb", "rw", "pb", "pw"]):
	make_datasets(names[0], names[1], start_time, count)

print "Writing big job CSV"

filename = 'mturk/CSVs/big_dataset.csv'
keys = big_dataset[0].keys()
with open(filename, 'wb') as output_file:
	dict_writer = csv.DictWriter(output_file, keys)
	dict_writer.writeheader()
	try:
		dict_writer.writerows(sample(big_dataset, len(big_dataset)))
	except UnicodeEncodeError:
		pass
print "Total elapsed time is " + elapsed(time.time(), start_time)



'''
if necessary, you can shuffle the dataset with the following code
it is important to shuffle the dataset because if mturk doesn't get through everything you then have a random sample

from random import sample

y = []
with open('big_dataset.csv', mode='r') as infile:
    x = csv.DictReader(infile)
    for row in x:
        y.append(row)
z = sample(y, len(y))

with open('big_dataset.csv', 'w') as outfile:
    dict_writer = csv.DictWriter(outfile, z[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(z)
