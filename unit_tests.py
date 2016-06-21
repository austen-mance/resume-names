from generator import * 

#my misc test file. not actually unit tests right now.....

apps_to_submit = load_scraper_data()

bk_data = []
bk_data.append(load_background_data("rb", "NYC")) 
bk_data.append(load_background_data("pb", "NYC"))

password = 'evanis#1'
username = 'careerpath5498@gmail.com'

#driver = login_to_acct(username, password)  #logs in with those details

info = get_one_app(apps_to_submit[0], bk_data[0], username) 

#info['resume'] = 3 #some number here

#update_resume(info)

#apply_to_job(driver, info)