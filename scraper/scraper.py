import requests
import csv
import time
import re

from docx import Document
from selenium import webdriver
from bs4 import BeautifulSoup
from random import sample

##############################################################################
#                         Variable Instantiation                             #
##############################################################################

dataset = []

NUMBER_OF_PAGES = 3


count = 1
addresses = range(0,19)
zipcodes = range(0,19)
resumes = range(0,8)
colleges = range(0,4)
firstnames = range(0,9)
lastnames = range(0,9)

##############################################################################
#   Instantiating Extensions (fuck ads, even if I'm not looking at them)     #
##############################################################################


custom_profile = webdriver.FirefoxProfile("uhwlqn5w.default")
driver = webdriver.Firefox(custom_profile)

##############################################################################
#                         Main Scraping Loop                                 #
##############################################################################

while count < (NUMBER_OF_PAGES):

    print "collecting " + str(count)

    driver.get("http://monster.com/jobs/search/?q=sales&where=chicago&page=" + str(count))

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

        jobAttrs['colleges'] = sample(colleges,4)
        jobAttrs['firstnames'] = sample(firstnames,4)
        jobAttrs['lastnames'] = sample(lastnames,4)
        jobAttrs['resumes'] = sample(resumes,4)
        jobAttrs['addresses'] = sample(addresses,4) 
        jobAttrs['zipcodes'] = sample(zipcodes,4)

        dataset.append(jobAttrs)

    count = count + 1

##############################################################################
#                         Save Data and Close                                #
##############################################################################


keys = dataset[0].keys()
with open('dataset.csv', 'wb') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(dataset)



