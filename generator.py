'''
Generator is our primary automated application system. This package takes an input of resume
PDFs and the scraper dataset (which should be produced as "dataset.csv") and applies to all
the jobs in that group.
'''

import csv
import time
import sys
import random
import datetime

from docx import Document
from selenium import webdriver

#status:
#update_resume == working
#login == working
#logout == under construction
#apply_to_job == under construction
#load_scraper_data == working
#load_background_data == working
#get_one_app ==working

##############################################################################
#               Application Functions (actually does the work)               #
##############################################################################


def update_resume(info):
    '''
    This function takes our resumes as input and modifies them
    as necessary to fit the applicant's details.
    '''
    resume = str(info['resume']) + '.docx' #grabs file

    document = Document("clerical/" + resume) #opens it

    for paragraph in document.paragraphs: #replaces info appropriately
        if '{NAME}' in paragraph.text:
            paragraph.text = info['firstname'] + " " + info['lastname']
        if '{EMAILADDRESS}' in paragraph.text:
            paragraph.text = 'Email: ' + info['email']
        if '{MAILADDRESS}' in paragraph.text:
            paragraph.text = info['address'][0] + info['address'][1] + info['address'][2]
        if '{UNIVERSITY}' in paragraph.text:
            paragraph.text = info['college']


    document.save('resume.docx') #saves to standard file - note concurrency impossible!

def login(email, password, logfile, app_round):
    '''
    Login uses selenium to log into monster and creates a driver object
    operated on by the other functions to submit applications.
    Returns the driver on success, and None on errors (and logs the reason)
    '''
    driver = webdriver.Firefox()

    try:
        driver.get("https://login.monster.com/Login/")

        driver.find_element_by_id("EmailAddress").clear()
        driver.find_element_by_id("EmailAddress").send_keys(email)
        time.sleep(random.gauss(1, 0.25))
        driver.find_element_by_id("Password").clear()
        driver.find_element_by_id("Password").send_keys(password)
        driver.find_element_by_id("btn-login").click()

        time.sleep(random.gauss(2, 0.5)) #to avoid ratelimiters & ensure loaded
        return driver #if login is successful, pass driver to next fn


    except:
        msg = str(app_round) + ", login failure: "
        logfile.write(msg + str(sys.exc_info()[0]) + "\n")
        return None #indicates that the login failed


    #Logging In

def logout(driver, logfile, app_round):
    '''
    Logs out of monster. Returns 1 on success and 0 on error (and logs it)
    '''
    try:
        driver.get("http://my.monster.com/Login/SignOut?fwr=true#")
    except:
        msg = str(app_round) + ", logout failure: "
        logfile.write(msg + str(sys.exc_info()[0]) + "\n")
        return 0
    return 1

def apply_to_job(driver, info, logfile, app_round):
    '''
    This code takes our information and uses it to submit applications
    '''

    #update information
    driver.get("http://my.monster.com/Profile/EditContactInformation?nav=1")
    time.sleep(random.gauss(2, 0.35))

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
        time.sleep(random.gauss(2, 0.3))

        driver.find_element_by_id("ctl01_hlApplyLink").click()
        time.sleep(random.gauss(2, 0.3))

        resumebox = driver.find_element_by_id("uploadedFile")
        resumebox.send_keys("resume.docx")

        driver.find_element_by_id("resumeSearchable").click()
        driver.find_element_by_id("Diversity").click()
        time.sleep(random.gauss(2, 0.25))
        driver.find_element_by_id("rbAuthorizedYes0").click()

        driver.find_element_by_id("btnSubmit").click()

        #time.sleep(random.gauss(3, 0.6))
        logfile.write(str(app_round) + ", ")

    except:
        msg = str(app_round) + ", Application " + str(app_round) + " failed: "
        logfile.write(msg + str(sys.exc_info()[0]) + "\n")
        return 0

    return 1

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
    (needs refactoring)
    '''
    data = {}

    if nametype == "pb":
        data['names'] = [line.strip().split(',') for line in open("names/names-pb.txt", 'r')]
        data['diverse'] = 1
        data['category'] = 0
        contact = open("bk-data/bm-contactdata.csv")

    elif nametype == "rb":
        data['names'] = [line.strip().split(',') for line in open("names/names-rb.txt", 'r')]
        data['diverse'] = 1
        data['category'] = 1
        contact = open("bk-data/bm-contactdata.csv")

    elif nametype == "pw":
        data['names'] = [line.strip().split(',') for line in open("names/names-pw.txt", 'r')]
        data['diverse'] = 0
        data['category'] = 2
        contact = open("bk-data/wm-contactdata.csv")

    elif nametype == "rw":
        data['names'] = [line.strip().split(',') for line in open("names/names-rw.txt", 'r')]
        data['diverse'] = 0
        data['category'] = 3
        contact = open("bk-data/wm-contactdata.csv")

    else:
        print "invalid name type entered"

    reader = csv.reader(contact)
    reader_list = list(reader)

    data['phones'] = reader_list[0]
    data['passwords'] = reader_list[1]
    data['emails'] = reader_list[2]

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
    '''
    Fugly function that returns the data structure for a single application
    after ingesting a group-structure.
    (needs refactoring)
    '''
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
#                    Logging and Similar Helper Functions                    #
##############################################################################
#note that logfiles do NOT cover data loading
#it must be manually managed

def create_logfile():
    '''
    Small stub function that creates a timestamped logfile and returns it's object
    '''
    curr_seconds = str(time.time()).split(".")[0][-5:] #gets current seconds of day
    logfile_id = str(datetime.date.today()) + "_" + curr_seconds

    logfile = open("logfile_"+ logfile_id + ".txt", "w")
    logfile.write("this is the logfile for application submissions on" + logfile_id + "\n")
    logfile.write("================================================================\n")

    return logfile

##############################################################################
#                          The Application Itself                            #
##############################################################################

def submit_applications(location, app_round=0):
    '''
    Our applier.

    'round' refers to the line of the dataset you start on, and is set as an int.
    By default it is 0, but can be altered if the program breaks/we get blocked.
    (a likely outcome)

    'nametype' refers to the type of applications we're sending. It takes rb/rw/pb/pw (two character
    strings) and sets the system appropriately - Rich/Poor Black/White

    'location' refers to the location of our applications. can be CHI/LAX/NYC (three char strs).
    This sets colleges/addresses, as with type.
    '''

    logfile = create_logfile() #creates a logging file

    apps_to_submit = load_scraper_data() #grabs data from dataset
    bk_data = []
    bk_data.append(load_background_data("rb", location)) #grabs data for each type of name
    bk_data.append(load_background_data("pb", location))
    bk_data.append(load_background_data("rw", location)) #working
    bk_data.append(load_background_data("pw", location))

    for types in bk_data: #lines
        password = random.choice(types['passwords'])  #grabs a random password
        email = random.choice(types['emails'])        #and a random email

        driver = login(email, password, logfile, app_round)  #logs in with those details

        if driver != None: #handles when login fails
            for elt in apps_to_submit: #for each app, iterate
                info = get_one_app(elt, types, email) #grab application

                update_resume(info) #update resume
                apply_to_job(driver, info, logfile, app_round) #apply
                app_round = app_round + 1

        logout(driver, logfile, app_round)

    driver.close()
    logfile.close()
