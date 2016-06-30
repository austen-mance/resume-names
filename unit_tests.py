#my misc test file. not actually unit tests right now.....

import random

from generator import *


logfile = create_logfile() #creates a logging file
account_data = load_account_data() #grabs account data            (list of dicts inc logins and names)
background_data = load_background_data("NYC") #grabs background data   (dict of lists inc. addresses and colleges)
scraper_data = load_scraper_data()

driver_round = 0
app_round = 0

account_elt = account_data[1]
scraper_elt = scraper_data[1]

driver = login(account_elt, logfile, app_round)

one_application = get_app_info(driver_round, background_data, scraper_elt, account_elt)

update_resume(one_application) #update resume


ze = apply_to_job(driver, one_application, logfile, app_round) #apply

app_round += 1

logfile.close()


