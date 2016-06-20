'''
Generator is our primary automated application system. This package takes an input of resume
PDFs and the scraper dataset (which should be produced as "dataset.csv") and applies to all
the jobs in that group.
'''

import csv
import time
import string
import sys
import random

from docx import Document
from selenium import webdriver

##############################################################################
#               The Helper Functions That Actually Do the Work               #
##############################################################################


def update_resume(elt, background_data):
    '''
    This function takes our resumes as input and modifies them
    as necessary to fit the applicant's details.
    '''
    resume = str(resume_num) + '.docx'

    document = Document(resume)

    for paragraph in document.paragraphs:
        if '{NAME}' in paragraph.text:
            paragraph.text = "Bob Newbie"
        if '{EMAILADDRESS}' in paragraph.text:
            paragraph.text = 'Email: ' + email
        if '{UNIVERSITY}' in paragraph.text:
            paragraph.text = university

    document.save('resume.docx')


def login_to_acct(email, password):
    driver = webdriver.Firefox()
    driver.get("https://login.monster.com/Login/")

    time.sleep(3) #to avoid ratelimiters & make sure the page loaded

    #Logging In
    driver.find_element_by_id("EmailAddress").clear()
    driver.find_element_by_id("EmailAddress").send_keys(email)
    time.sleep(1)

    driver.find_element_by_id("Password").clear()
    driver.find_element_by_id("Password").send_keys(password)

    submitbox = driver.find_element_by_id("signInContent").find_element_by_xpath("//input[@data-value='SIGN IN']").click()

    return driver


def apply_to_job(driver, info):
    '''
    This code takes our information and uses it to submit applications
    '''


    #update information
    driver.get("http://my.monster.com/Profile/EditContactInformation?nav=1")
    time.sleep(2)

    driver.find_element_by_id("FirstName").clear()
    driver.find_element_by_id("FirstName").send_keys(info['firstname'])

    driver.find_element_by_id("LastName").clear()
    driver.find_element_by_id("LastName").send_keys(info['lastname'])

    driver.find_element_by_id("Address_Address").clear()
    driver.find_element_by_id("Address_Address").send_keys(info['address'][0])

    driver.find_element_by_id("Address_UserEnteredZipName").clear()
    driver.find_element_by_id("Address_UserEnteredZipName").send_keys(info['address'][1])

    driver.find_element_by_id("Phones_0__Number").clear()
    #driver.find_element_by_id("Phones_0__Number").send_keys("493-103-1033")

    driver.find_element_by_xpath("//input[@data-value='Save']").click()



    #apply for the job

    try:
        driver.get(info['link'])
        time.sleep(2)

        driver.find_element_by_id("ctl01_hlApplyLink").click()
        time.sleep(2)

        resumebox = driver.find_element_by_id("uploadedFile")
        resumebox.send_keys("/Volumes/Data/code/resume-names/5.docx")

        driver.find_element_by_id("resumeSearchable").click()
        driver.find_element_by_id("Diversity").click()
        time.sleep(3)
        driver.find_element_by_id("rbAuthorizedYes0").click()

    #driver.find_element_by_id("btnSubmit").click()

        time.sleep(4)
        return 1 #returns 1 on success

    except:
        print "Application #-# failed for reason", sys.exc_info()[0]
        return 0


def load_scraper_data():
    '''
    This function takes the csv file "dataset.csv" created by the scraper
    and unpacks it to a set of instructions the application system can use.
    '''
    appset = []

    with open('dataset.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for elt in reader:
            jobapp = {}
            jobapp['firstnames'] = map(int, elt['firstnames'][1:-1].split(','))
            jobapp['colleges'] = map(int, elt['colleges'][1:-1].split(','))
            jobapp['lastnames'] = map(int, elt['lastnames'][1:-1].split(','))
            jobapp['resumes'] = map(int, elt['resumes'][1:-1].split(','))
            jobapp['addresses'] = map(int, elt['addresses'][1:-1].split(','))
            jobapp['zipcodes'] = map(int, elt['zipcodes'][1:-1].split(','))
            jobapp['link'] = elt['link']

            appset.append(jobapp)
    return appset

def load_background_data(nametype, location):
    '''
    This function pulls out our background information from files: namely the names,
    addresses, zipcodes etc and saves them to a series of lists so they can be used by the main
    program.
    '''
    data = {}

    if nametype == "pb":
        data['names'] = [line.strip().split(',') for line in open("names/names-pb.txt", 'r')]
        data['diverse'] = 1
        data['category'] = 0

        contact = open("bk-data/bm-contactdata.csv")
        reader = csv.reader(contact)
        l2 = list(reader)
        
        data['phones'] = l2[0]
        data['passwords'] = l2[1]
        data['emails'] = l2[2]

    elif nametype == "rb":
        data['names'] = [line.strip().split(',') for line in open("names/names-rb.txt", 'r')]
        data['diverse'] = 1
        data['category'] = 1

        contact = open("bk-data/bm-contactdata.csv")
        reader = csv.reader(contact)
        l2 = list(reader)

        data['phones'] = l2[0]
        data['passwords'] = l2[1]
        data['emails'] = l2[2]

    elif nametype == "pw":
        data['names'] = [line.strip().split(',') for line in open("names/names-pw.txt", 'r')]
        data['diverse'] = 0
        data['category'] = 2

        contact = open("bk-data/wm-contactdata.csv")
        reader = csv.reader(contact)
        l2 = list(reader)

        data['phones'] = l2[0]
        data['passwords'] = l2[1]
        data['emails'] = l2[2]

    elif nametype == "rw":
        data['names'] = [line.strip().split(',') for line in open("names/names-rw.txt", 'r')]
        data['diverse'] = 0
        data['category'] = 3

        contact = open("bk-data/wm-contactdata.csv")
        reader = csv.reader(contact)
        l2 = list(reader)

        data['phones'] = l2[0]
        data['passwords'] = l2[1]
        data['emails'] = l2[2]

    else:
        print "invalid name type entered"

    if location == "CHI":
        data['addresses'] = [line.strip().split(',') for line in open("bk-data/chicago/add-zip.txt", 'r')]
        data['colleges'] = [line.strip() for line in open("bk-data/chicago/colleges.txt", 'r')]
    elif location == "NYC":
        data['addresses'] = [line.strip().split(',') for line in open("bk-data/nyc/add-zip.txt", 'r')]
        data['colleges'] = [line.strip() for line in open("bk-data/nyc/colleges.txt", 'r')]
    elif location == "LAX":
        data['addresses'] = [line.strip().split(',') for line in open("bk-data/lax/add-zip.txt", 'r')]
        data['colleges'] = [line.strip() for line in open("bk-data/lax/colleges.txt", 'r')]
    else:
        print "invalid location entered"
    return data


def get_one_app(selection, types, email):

    category = types['category']

    one_app = {}

    one_app['email'] = email
    one_app['address'] = types['addresses'][selection['addresses'][category]]

    one_app['college'] = types['colleges'][selection['colleges'][category]]

    one_app['firstname'] = types['names'][selection['firstnames'][category]][0]
    one_app['lastname'] = types['names'][selection['lastnames'][category]][1]

    one_app['link'] = selection['link']

    one_app['resume'] = selection['resumes'][category]

    return one_app


##############################################################################
#                          The Application Itself                            #
##############################################################################


def submit_applications(location, round=0):
    '''
    Our application code.

    'round' refers to the line of the dataset you start on, and is set as an int.
    By default it is 0, but can be altered if the program breaks/we get blocked.
    (a likely outcome)

    'nametype' refers to the type of applications we're sending. It takes rb/rw/pb/pw (two character
    strings) and sets the system appropriately - Rich/Poor Black/White

    'location' refers to the location of our applications. can be CHI/LAX/NYC (three char strs).
    This sets colleges/addresses, as with type.
    '''

    apps_to_submit = load_scraper_data() #grabs data from dataset
    bk_data = []
    bk_data.append(load_background_data("rb", location)) #grabs data for each type of name
    bk_data.append(load_background_data("pb", location))
    bk_data.append(load_background_data("rw", location))
    bk_data.append(load_background_data("pw", location))



    for types in bk_data:
        password = random.choice(types['passwords'])  #grabs a random password
        email = random.choice(types['emails'])        #and a random email

        driver = login_to_acct(email, password)  #logs in with those details

        for elt in apps_to_submit: #for each app, iterate
            info = get_one_app(elt, types, email) #grab application

            update_resume(info) #update resume
            apply_to_job(driver, info) #apply

        #logout here

    driver.close()



"http://my.monster.com/Login/SignOut?fwr=true#"
