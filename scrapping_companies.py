import pandas as pd 
print("scrapping companies")
annonces = pd.read_csv('df_new_pymongo_no_duplicate.csv',encoding='utf-8')

def generate_delay():
    """
    retourn un chiffre aléatoire suivant une distribution normal de moyenne 4 secondes et d'ecart-type de 0.8
    Ce chiffre aléatoire est le délai après chaque clique. Le but est de simuler le comportement d'un humain :
    un délai fixe peut attirer l'attention des contrôleurs, tout comme un délai aléatoire d'une distribution uniforme
    """
    mean = 4
    sigma = 0.8
    return np.random.normal(mean,sigma,1)[0]

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import numpy as np
from pymongo import MongoClient
client = MongoClient('localhost') #importe local host de mongodb
db = client.new_indeed_raw # connection à la table JobPosting
companyk = db.companies 
import pandas as pd
import datetime
#browser=webdriver.Chrome('C:\\Users\\Administrateur\\Anaconda3\\Scripts')
browser = webdriver.Firefox()

import time
import numpy as np

import pandas as pd
import datetime
#browser.get("https://www.linkedin.com/")
#company_name = "procter and gamble"

#browser.get("https://www.linkedin.com/search/results/companies/?keywords="+company_name+"&origin=SWITCH_SEARCH_VERTICAL")

#links = browser.find_elements_by_css_selector("h3[class='search-result__title t-16 t-black t-bold']")
#links[0].text

#time.sleep(generate_delay())
#print(links[0].text)
#links[0].click()
#time.sleep(generate_delay()) 

for idx, i in enumerate(annonces["Company"].loc[annonces["Company"].notnull()].unique()):
    if companyk.find_one({'company':"'"+i+"'"})==None:
        company_name = "'"+i+"'"
        print(i)
        try:
            browser.get("https://duckduckgo.com/?q="+company_name+"+%22entreprises.lefigaro.fr%22&t=h_&ia=web")
            browser.maximize_window()
            links = browser.find_elements_by_css_selector("a[class='result__a']")
        except:
            print("could not find research")
            pass      
        try:
            links[0].click()
            time.sleep(generate_delay())
        except:
            print("could not click on the link")
            pass
        try:
            industry = browser.find_element_by_class_name("openData").text
        except:
            print("could not fetch industry")
            industry = np.nan
            pass
        time.sleep(generate_delay())
        try: #fill the dataframe on the ro
            companyk.insert_one({"company":company_name,"info":industry});
        except:
            print("could not uplaod")
            pass

        
    



  
