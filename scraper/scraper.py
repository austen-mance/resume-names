import requests
import csv
import time
import re
import pandas as pd

from docx import Document
from selenium import webdriver
from bs4 import BeautifulSoup
from random import sample


##############################################################################
#                         Variable Instantiation                             #
##############################################################################

dataset = []

# this seems to max out around 45 pages for most job/city pairs
# however, there are only 25 pages of Chicago clerical

NUMBER_OF_PAGES = 26

addresses = range(0,19)
zipcodes = range(0,19)
resumes = range(0,8)
colleges = range(0,4)
firstnames = range(0,9)
lastnames = range(0,9)

urls = {"http://www.monster.com/jobs/search/Full-Time_8?q=sales&where=New-York__2c-NY&page=": ['New York', 'Sales'],"www.monster.com/jobs/search/Full-Time_8?q=sales&where=Chicago__2c-IL&page=": ['Chicago', 'Sales'], "http://www.monster.com/jobs/search/?q=sales&where=Los-Angeles__2C-CA&page=": ["Los Angeles", "Sales"],"http://www.monster.com/jobs/search/Full-Time_8?q=clerical&where=Chicago__2c-IL&page=": ["Chicago", "Clerical"],"http://www.monster.com/jobs/search/Full-Time_8?q=clerical&where=New-York__2c-NY&page=": ["New York", "Clerical"],"http://www.monster.com/jobs/search/?q=clerical&where=Los-Angeles__2C-CA&page=":["Los Angeles", "Clerical"]}


##############################################################################
#   Instantiating Extensions (fuck ads, even if I'm not looking at them)     #
##############################################################################


custom_profile = webdriver.FirefoxProfile("mhqbalam.default")
driver = webdriver.Firefox(custom_profile)

##############################################################################
#                         Main Scraping Loop                                 #
##############################################################################
for url in urls.keys():
	count = 1
	while count < (NUMBER_OF_PAGES):

	    print "collecting page " + str(count) + " of " + urls[url][0] + " " + urls[url][1]

	    driver.get(url + str(count))

	    source_code = driver.find_element_by_xpath("//*").get_attribute("outerHTML")
	    soup = BeautifulSoup(source_code)

	    jobs = soup.find_all("article") #gets list of 25 jobs 


	    for elt in jobs:
	        jobAttrs = {}

	        jobAttrs['link'] = elt.find("a")['href']
	        jobAttrs['title'] = elt.find("div", class_="jobTitle").get_text().encode('ascii', 'ignore')
	        jobAttrs["company"] = elt.find("div", class_="company").get_text().encode('ascii', 'ignore')
	        jobAttrs["location"] = elt.find("div", class_="location").get_text().encode('ascii', 'ignore')
	        jobAttrs["preview"] = elt.find("div", class_="preview").get_text().encode('ascii', 'ignore')
	        jobAttrs['link'] = elt.find("a")['href'].split('?',1)[0]
	        jobAttrs['original_link'] = elt.find("a")['href']
	        jobAttrs['title'] = elt.find("div", class_="jobTitle").get_text().encode('ascii','ignore')
	        jobAttrs["company"] = elt.find("div", class_="company").get_text().encode('ascii','ignore')
	        jobAttrs["location"] = elt.find("div", class_="location").get_text().encode('ascii','ignore')
	        jobAttrs["preview"] = elt.find("div", class_="preview").get_text().encode('ascii','ignore')
	        jobAttrs['full'] = str(elt)
	        jobAttrs['colleges'] = sample(colleges,4)
	        jobAttrs['firstnames'] = sample(firstnames,4)
	        jobAttrs['lastnames'] = sample(lastnames,4)
	        jobAttrs['resumes'] = sample(resumes,4)
	        jobAttrs['addresses'] = sample(addresses,4) 
	        jobAttrs['zipcodes'] = sample(zipcodes,4)
	        jobAttrs['type'] = urls[url][1].lower()
	        jobAttrs['city'] = urls[url][0]

	        dataset.append(jobAttrs)

	    count = count + 1

##############################################################################
#                         Save Data and Close                                #
##############################################################################

#df = pd.DataFrame()
#for data in dataset:
#	df.append(pd.DataFrame.from_dict(data))
#df.to_csv('dataset.csv')

keys = dataset[0].keys()
with open('dataset.csv', 'wb') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    try:
    	dict_writer.writerows(dataset)
    except UnicodeEncodeError:
		pass


