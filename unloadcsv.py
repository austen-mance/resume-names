import csv

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
