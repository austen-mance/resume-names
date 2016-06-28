#my misc test file. not actually unit tests right now.....

import random

#apps_to_submit = load_scraper_data()

#bk_data = []
#bk_data.append(load_background_data("rb", "NYC")) 
#bk_data.append(load_background_data("pb", "NYC"))

#password = 'evanis#1'
#username = 'careerpath5498@gmail.com'

#driver = login_to_acct(username, password)  #logs in with those details

#info = get_one_app(apps_to_submit[0], bk_data[0], username) 

#info['resume'] = 3 #some number here

#update_resume(info)

#apply_to_job(driver, info)


df = [line.strip().split(',') for line in open("accounts.csv", 'r')] #set of account details
pb = []
pw = []
rb = []
rw = []
subset = [] #sublists for each

#sorts into 4 separate lists
for elt in df:
    if elt[5] == "pb":
        pb.append(elt)
    elif elt[5] == "rb":
        rb.append(elt)
    elif elt[5] == "pw":
        pw.append(elt)
    elif elt[5] == "rw":
        rw.append(elt)

subset.append(random.choice(pb))
subset.append(random.choice(rb))
subset.append(random.choice(pw))
subset.append(random.choice(rw)) 