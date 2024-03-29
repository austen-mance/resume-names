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
import re
import os

from docx import Document
from selenium import webdriver

##############################################################################
#                          Selenium Functions                                #
##############################################################################

def login(account_elt, logfile, app_round):
    '''
    Login uses selenium to log into monster and creates a driver object
    operated on by the other functions to submit applications.
    Returns the driver on success, and None on errors (and logs the reason)
    '''

    path = get_path()
    adblockfile = os.path.join(path, 'firefox-profile/abp-2.7.3.xpi')
    ffprofile = webdriver.FirefoxProfile()
    ffprofile.add_extension(adblockfile)
    driver = webdriver.Firefox(ffprofile)

    try:
        driver.get("https://login.monster.com/Login/")

        driver.find_element_by_id("EmailAddress").clear()
        driver.find_element_by_id("EmailAddress").send_keys(account_elt['email'])
        time.sleep(random.gauss(1, 0.25))
        driver.find_element_by_id("Password").clear()
        driver.find_element_by_id("Password").send_keys(account_elt['password'])
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
    driver.get(info['link'])
    time.sleep(random.gauss(2, 0.3))

    type1 = usable_element(driver, "PrimaryJobApply")
    type2 = usable_element(driver, "ctl01_hlApplyLink")

    if type1 != None:
        type1.click()
        return apply_t1(driver, info, logfile, app_round)

    elif type2 != None:
        type2.click()
        return apply_t2(driver, logfile, app_round)

    else:
        logfile.write(str(app_round) + ", failed: apply btn not found")
        return 0

def apply_t1(driver, info, logfile, app_round):
    '''
    The selenium application code that covers one newer application form type
    '''

    time.sleep(random.gauss(2, 0.3))

    sjw_options(driver)

    time.sleep(random.gauss(0.5, 0.15))

    click_if_usable(driver, "Pi_WorkAuthorizationStatusTrue")


    geo_elt = usable_element(driver, "Pi_UserEnteredGeoName")
    if geo_elt != None:
        zipcode = re.sub("[^0-9]", "", info['address'][2])
        geo_elt.send_keys(zipcode)
        geo_elt.submit()

    click_if_usable_by_xpath(driver, "//a[@href='#AddResume']")

    attachment_elt = usable_element(driver, "Attachments")
    if attachment_elt != None: #base case
        current_path = get_path()
        current_path = current_path + "/resume.docx"
        attachment_elt.send_keys(current_path)
    else:
        logfile.write(str(app_round) + ", failed: resume upload failed")
        return 0

    time.sleep(random.gauss(2, 0.25))

    submitted = 0
    submitted += click_if_usable(driver, "btnSubmit")
    submitted += click_if_usable(driver, "applybtn")

    if submitted == 0:
        logfile.write(str(app_round) + ", failed: submit btn not found")
        return 0

    time.sleep(random.gauss(1, 0.6))
    logfile.write(str(app_round) + ", ")
    return 1

def apply_t2(driver, logfile, app_round):
    '''
    The selenium application code that covers one older application form type
    '''

    click_if_usable(driver, "lnkEdit")
    click_if_usable(driver, "linkEdit")
    click_if_usable(driver, "jvResumeUpload-tab")

    if len(driver.find_elements_by_id("uploadedFile")) != 0: #base case
        click_if_usable(driver, "jvUploadTab")
        resumebox = usable_element(driver, "uploadedFile")
        if resumebox != None:
            current_path = get_path()
            current_path = current_path + "/resume.docx"
            resumebox.send_keys(current_path)

        resume_name_box = usable_element(driver, "nameNewResume")
        if resume_name_box != None:
            resume_name_box.send_keys("resume")

    else:
        logfile.write(str(app_round) + ", failed: resume upload failed")
        return 0


    time.sleep(random.gauss(2, 0.3))
    sjw_options(driver)

    click_if_usable(driver, "rbAuthorizedYes0")
    click_if_usable_by_xpath(driver, "//button[@title='Save Changes']")

    submitted = 0
    submitted += click_if_usable(driver, "btnSubmit")
    submitted += click_if_usable(driver, "applybtn")

    if submitted == 0:
        logfile.write(str(app_round) + ", failed: submit btn not found")
        return 0

    time.sleep(random.gauss(1, 0.6))
    logfile.write(str(app_round) + ", ")
    return 1

def sjw_options(driver):
    '''
    Little module that handles the various SJW options the feds require
    '''

    click_if_usable(driver, "Rs_DiversityMember")#t1
    click_if_usable(driver, "Rs_SearchableMuember")#t1

    click_if_usable(driver, "resumeSearchable")#t2
    click_if_usable(driver, "Diversity")#t2

    click_if_usable(driver, "ethnP_8")#t2
    click_if_usable(driver, "ethn_6")#t1

    gender_dropdown = usable_element(driver, "ddlGender")
    if gender_dropdown != None: #if usable
        select_dropdown(driver, "ddlGender", "-1")

##############################################################################
#                        Selenium Helper Functionsc                           #
##############################################################################

def usable_element(driver, element_tag):
    '''
    returns false if unusable, and the element object (true) if usable
    '''
    elt = driver.find_elements_by_id(element_tag)
    if len(elt) != 0 and elt[0].is_displayed() == True:
        return elt[0]
    else:
        return None

def click_if_usable(driver, element_tag):
    '''
    little helper function that clicks an element iff it's visible and exists.
    returns 1 if successful and 0 otherwise.
    '''
    elt = driver.find_elements_by_id(element_tag)
    if len(elt) != 0 and elt[0].is_displayed() == True:
        elt[0].click()
        return 1
    else:
        return 0

def click_if_usable_by_xpath(driver, xpath):
    '''
    Same as click_if_usable, but with xpaths
    '''
    elt = driver.find_elements_by_xpath(xpath)
    if len(elt) != 0 and elt[0].is_displayed() == True:
        elt[0].click()
        return 1
    else:
        return 0

def select_dropdown(driver, dropdown_id, option_value):
    '''
    helper function for clicking on dropdown menu elements
    '''
    dd = driver.find_element_by_id(dropdown_id)
    xpath = ".//option[@value='{}']".format(option_value)
    dd.find_element_by_xpath(xpath).click()
##############################################################################
#                       Data Management Functions                            #
##############################################################################

def load_account_data():
    '''
    loads account data
    '''
    with open('accounts.csv') as f:
        df = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]

    pb, pw, rb, rw, subset = [], [], [], [], [] #sublists for each

    #sorts into 4 separate lists
    for elt in df:
        if elt['category'] == "pb":
            pb.append(elt)
        elif elt['category'] == "rb":
            rb.append(elt)
        elif elt['category'] == "pw":
            pw.append(elt)
        elif elt['category'] == "rw":
            rw.append(elt)

    subset.append(random.choice(pb))
    subset.append(random.choice(rb))
    subset.append(random.choice(pw))
    subset.append(random.choice(rw))

    #now we have a subsetted list
    return subset

def load_background_data(location):
    '''
    This function pulls out our background information from files: namely the names,
    addresses, zipcodes etc and saves them to a series of lists so they can be used by the main
    program.
    '''
    data = {}

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

def load_scraper_data():
    '''
    This function takes the csv file "dataset.csv" created by the scraper
    and unpacks it to a set of instructions the application system can use.
    '''
    appset = []

    with open('scraper/dataset.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for elt in reader:
            jobapp = {}
            jobapp['colleges'] = map(int, elt['colleges'][1:-1].split(','))
            jobapp['resumes'] = map(int, elt['resumes'][1:-1].split(','))
            jobapp['addresses'] = map(int, elt['addresses'][1:-1].split(','))
            jobapp['zipcodes'] = map(int, elt['zipcodes'][1:-1].split(','))
            jobapp['link'] = elt['link']
            jobapp['type'] = elt['type']

            appset.append(jobapp)
    return appset

def get_app_info(driver_round, background_data, scraper_elt, account_elt):
    '''
    Fugly function that returns the data structure for a single application
    after ingesting a group-structure.
    '''

    one_app = {}

    #first get the number of each
    address_number = scraper_elt["addresses"][driver_round]
    college_number = scraper_elt["colleges"][driver_round]
    resume_number = scraper_elt['resumes'][driver_round]


    #then grab the relevant info from the DBs
    one_app['link'] = scraper_elt['link']
    one_app['type'] = scraper_elt['type']

    one_app['email'] = account_elt['email']
    one_app['firstname'] = account_elt['firstname']
    one_app['lastname'] = account_elt['lastname']

    one_app['address'] = background_data['addresses'][address_number]
    one_app['college'] = background_data['colleges'][college_number]
    one_app['resume'] = resume_number

    return one_app

def update_resume(info):
    '''
    This function takes our resumes as input and modifies them
    as necessary to fit the applicant's details.
    '''
    resume = str(info['resume']) + '.docx' #grabs file
    document = Document(info['type'] + "/" + resume) #opens it

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

##############################################################################
#                    Logging and Similar Helper Functions                    #
##############################################################################

def create_logfile():
    '''
    Small stub function that creates a timestamped logfile and returns it's object
    '''
    curr_seconds = str(time.time()).split(".")[0][-5:] #gets current seconds of day
    logfile_id = str(datetime.date.today()) + "_" + curr_seconds

    logfile = open("logs/logfile_"+ logfile_id + ".txt", "w")
    logfile.write("this is the logfile for application submissions on" + logfile_id + "\n")
    logfile.write("================================================================\n")

    return logfile

def get_path():
    '''
    Gets directory path (necessary for abs. path resume upload)
    '''
    path = os.path.dirname(os.path.realpath(__file__))
    return path

##############################################################################
#                       The Main Applier Funciton                            #
##############################################################################

def submit_applications(location, app_round=0, driver_round=0):
    '''
    Our applier.
    'location' refers to the location of our applications. can be CHI/LAX/NYC (three char strs).
    This sets colleges/addresses.

    'app_round' refers to the line of the dataset you start on, and is set as an int.
    By default it is 0, but can be altered if the program breaks/we get blocked.
    (a likely outcome)
    '''

    logfile = create_logfile() #creates a logging file
    account_data = load_account_data() #grabs account data            (list of dicts inc logins and names)
    background_data = load_background_data(location) #grabs background data   (dict of lists inc. addresses and colleges)
    scraper_data = load_scraper_data()

    driver_round = 0
    for account_elt in account_data:
        driver = login(account_elt, logfile, app_round) #login

        if driver != None: #handles when login fails
            for scraper_elt in scraper_data:

                #grab information for one application
                one_application = get_app_info(driver_round, background_data, scraper_elt, account_elt)

                update_resume(one_application) #update resume
                apply_to_job(driver, one_application, logfile, app_round) #apply

                app_round += 1

        logout(driver, logfile, app_round) #logout

        driver_round += 1
        app_round = 0

    driver.close()
    logfile.close()

