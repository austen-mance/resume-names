'''
Generator is our primary automated application system. This package takes an input of resume
PDFs and the scraper dataset (which should be produced as "dataset.csv") and applies to all
the jobs in that group.
'''

import csv
import time
import string

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

    time.sleep(4) #to avoid ratelimiters & make sure the page loaded

    #Logging In
    driver.find_element_by_id("EmailAddress").clear()
    driver.find_element_by_id("EmailAddress").send_keys("careerpath5498@gmail.com")

    driver.find_element_by_id("Password").clear()
    driver.find_element_by_id("Password").send_keys("winter2016econ")

    submitbox = driver.find_element_by_id("signInContent").find_element_by_xpath("//input[@data-value='SIGN IN']").click()

    return driver


def apply_to_job(driver):
    '''
    This code takes our information and uses it to submit applications
    '''
    driver.get("http://my.monster.com/Profile/EditContactInformation?nav=1")
    time.sleep(2)

    driver.find_element_by_id("FirstName").clear()
    driver.find_element_by_id("FirstName").send_keys("BoB")

    driver.find_element_by_id("LastName").clear()
    driver.find_element_by_id("LastName").send_keys("Newbie")

    driver.find_element_by_id("Address_Address").clear()
    driver.find_element_by_id("Address_Address").send_keys("604 Terry Drive, Joliet IL")

    '''
    driver.find_element_by_id("Address_UserEnteredZipName").clear()
    driver.find_element_by_id("Address_UserEnteredZipName").send_keys("60435")
    '''

    driver.find_element_by_id("Phones_0__Number").clear()
    driver.find_element_by_id("Phones_0__Number").send_keys("493-103-1033")

    driver.find_element_by_xpath("//input[@data-value='Save']").click()

    #and now we apply for the actual job
    driver.get("http://jobview.monster.com/Sales-Account-Executive-150k-potential-Job-San-Diego-CA-US-163096744.aspx")
    time.sleep(3)

    driver.find_element_by_id("ctl01_hlApplyLink").click()
    time.sleep(3)

    resumebox = driver.find_element_by_id("uploadedFile")
    resumebox.send_keys("/Volumes/Data/code/resume-names/5.docx")

    driver.find_element_by_id("resumeSearchable").click()
    driver.find_element_by_id("Diversity").click()
    time.sleep(2)
    driver.find_element_by_id("rbAuthorizedYes0").click()

    #driver.find_element_by_id("btnSubmit").click()

    time.sleep(5)


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
    elif nametype == "rb":
        data['names'] = [line.strip().split(',') for line in open("names/names-rb.txt", 'r')]
        data['diverse'] = 1
        data['category'] = 1
    elif nametype == "pw":
        data['names'] = [line.strip().split(',') for line in open("names/names-pw.txt", 'r')]
        data['diverse'] = 0
        data['category'] = 2
    else:
        data['names'] = [line.strip().split(',') for line in open("names/names-rw.txt", 'r')]
        data['diverse'] = 0
        data['category'] = 3

    if location == "CHI":
        data['addresses'] = [line.strip().split(',') for line in open("chicago/add-zip.txt", 'r')]
        data['colleges'] = [line.strip() for line in open("chicago/colleges.txt", 'r')]
    elif location == "NYC":
        data['addresses'] = [line.strip().split(',') for line in open("nyc/add-zip.txt", 'r')]
        data['colleges'] = [line.strip() for line in open("nyc/colleges.txt", 'r')]
    else:
        data['addresses'] = [line.strip().split(',') for line in open("lax/add-zip.txt", 'r')]
        data['colleges'] = [line.strip() for line in open("lax/colleges.txt", 'r')]

    return data


##############################################################################
#                          The Application Itself                            #
##############################################################################


def submit_applications(nametype, location, round=0):
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

    apps_to_submit = load_scraper_data()
    background_data = load_background_data(nametype, location)


    driver = login_to_acct(email, password)

    for elt in apps_to_submit:
        update_resume(elt,background_data)
        apply_to_job(driver)

    driver.close()



"http://my.monster.com/Login/SignOut?fwr=true#"
