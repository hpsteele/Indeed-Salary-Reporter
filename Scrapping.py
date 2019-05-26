"""
Ce code permet de scrapper le site cible en utilisant selenium
Il est toujours en développement. L'idée est de l'optimiser et de construire des classes. Nous venons de changer la méthoe de scraping en utilisant urllib et beautifulsoup 
"""


import threading
from threading import Thread, Lock
import time
from random import choice as rchoice
import random
import pandas as pd 
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import numpy as np
client = MongoClient('localhost') #importe local host de mongodb
db = client.new_indeed_raw # connection à la table 
new_indeed_hope = db.new_indeed_hope 

keyword='aws or apache or hortonworks or talend or teradata or mariadb or postgres'
keywords = keyword
city = ["Lyon","Toulouse","Nantes","Bordeaux","Paris"] #définition de la liste de ville cible
estimated = ""
count=0
df_counter = pd.read_csv('C:/Users/Administrateur/Documents/SIMPLONr/df_counter.csv', sep=',', encoding='utf-8' )
import numpy as np

def generate_delay():
    """
    retourn un chiffre aléatoire suivant une distribution normal de moyenne 4 secondes et d'ecart-type de 0.8
    Ce chiffre aléatoire est le délai après chaque clique. Le but est de simuler le comportement d'un humain :
    un délai fixe peut attirer l'attention des contrôleurs, tout comme un délai aléatoire d'une distribution uniforme
    """
    mean = 4
    sigma = 0.8
    return np.random.normal(mean,sigma,1)[0]




time.sleep(generate_delay())
time.sleep(generate_delay())
timestamp = datetime.datetime.today().strftime('%Y-%m-%d')  #définition du timestamp qui sera utilisé dans le jour du scraping
import time
from random import choice as rchoice
import random
import pandas as pd 
#Définition du dataframe
df_indeed = pd.DataFrame({'Title' : [],'Details' : [],'Link' : [],'Company' : [],'Location' : [],'Estimated Salary' : [],'date' : [],'timestamp' : [],'detailslocconcat' : [],"url": []})



 
#Def de la fonction pour écrire le texte dans le field recherche
"""Entrée: la fonction prend 3 paramètres en entrée:
    Parameter choice: il s'agit de la ville. La fonction utilise la ville lors de la déclaration du website
    Parameter count : le compteur va déclencher la fonction switch_city à partir de l'incrémentation 89
    Parameter page2 :  le compteur utilise la variable page2, qui sera incrémentée 
    Action : Cette fonction sert à choisir la page de recherche
    Output : changement de la page de recherche. Déclenchement de la fonction city_switch sur la 90ème page 
    """
def pagination(choice,count,pages2,website,browser,keywords,skills,thread_id):
    """Input
    Parameter:
    Parameter:
    Output
    """
    pagination.counter += 1 #incrémentation du compteur de la fonction
    print("counter pagination!"+str(pagination.counter)) 
    pages2 = "&start="+str(count)+"0"    # page output
    print("my count var is "+str(count))

    current = browser.current_window_handle
    multi_window = browser.window_handles
    for window in multi_window:
        if window != current: #regarde si une nouvelle fenetre est ouvert
            browser.switch_to.window(window)  #va sur l'autre fenêtre ouverte
            browser.close() #ferme cette fenêtre
            browser.switch_to.window(current)
    while count<90: #si le compteur est > 90, il changera de ville
        count += 1
        try:
            browser.get(website)
            print(choice)
        except:
            browser.get(website)
            print("error on pagination function")
            time.sleep(generate_delay())
        randomize_click(choice,count,website,browser,keywords,skills,thread_id)   #repart sur la fonction initiale
    switch_city(count,website,browser,keywords,skills,thread_id)#repart sur la fonction initiale
    



def randomize_click(choice,count,website,browser,keywords,skills,thread_id):
"""Entrée: la fonction prend 2 paramètres en entrée:
    Parameter choice: il s'agit de la ville. La fonction utilise la ville lors de la déclaration du website
    Parameter count : la fonction prend le paramètre count [mais ne l'utilise pas ]
    
    Action : Cette fonction sert à choisir aléatoirement le lien sur lequel cliquer pour reproduire le comportement d'un humain 
    Output : la fonction va renvoyer la variable i qui sera utilisée lors du scraping 
    """
    pages2 = "&start="+str(count)+"0"
    website = "https://www.indeed.fr/emplois?q="+str(keyword)+str(estimated)+"&l="+str(choice)+str(pages2)
    browser.get(website)
    links = browser.find_elements_by_class_name('jobtitle')  #définit la liste d'élements
    randompage = [len(links)]#randompage is a random number to state the number
    number = [i for i in range(random.choice(randompage))] #number also decide of the number of iterations
    #linkswith_duplicates = browser.find_elements_by_xpath("//a[%s]" % condition)
    for i in range(len(links)):
        while number != []:
            choice_num = random.choice(number)#choice_num prend un le nom d'une numbre entre 0 et 15 pour éviter d'ouvrir les pages l'une après l'autre
            number.remove(choice_num) #enlève ce numéro de la liste
            i = choice_num 
            scraping_jobpost(i,choice,pages2,website,browser,keywords,skills,thread_id)
            
        pagination(choice,count,pages2,website,browser,keywords,skills,thread_id)




def switch_city(count,website,browser,keywords,skills,thread_id):
"""Entrée: la fonction prend 3 paramètres en entrée:
    Parameter choice: il s'agit de la ville. La fonction utilise la ville lors de la déclaration du website
    Parameter count : le compteur va déclencher la fonction switch_city à partir de l'incrémentation 89
    Parameter page2 :  le compteur utilise la variable page2, qui sera incrémentée 
    Action : Cette fonction sert à choisir la page de recherche
    Output : changement de la page de recherche. Déclenchement de la fonction city_switch sur la 90ème page 
    """
    #count = 1 #reset the var count to 0
    keywords = keyword
    keywords = random.choice(skills)#choice prend un le nom d'une ville dans la liste de villes 
    time.sleep(generate_delay())
    print(keywords)
    city.remove(keywords)# efface la ville selectionnée de la liste
    randomize_click(choice,count,website,browser,keywords,skills,thread_id)   #repart sur la fonction initiale

#Def de la fonction scraping
def scraping_jobpost(i,choice,pages2,website,browser,keywords,skills,thread_id):
"""Entrée: la fonction prend 3 paramètres en entrée:
    Parameter choice: il s'agit de la ville. La fonction utilise la ville lors de la déclaration du website
    Parameter i : le numéro aléatoire du lien défini dans la fonction randomize click 
    Parameter page2 :  le compteur utilise la variable page2, qui sera incrémentée 
    Action : Cette fonction sert à scraper l'information et à ajouter les données dans la base de données, si l'info n'est pas présente
    """
    website = "https://www.indeed.fr/emplois?q="+str(keyword)+str(estimated)+"&l="+str(choice)+str(pages2)
    browser.set_window_size("3024", "3024")
    links = browser.find_elements_by_class_name('jobtitle')
    try:
        browser.execute_script("arguments[0].scrollIntoView();", links[i])
        browser.execute_script("window.scrollBy(0, -250);")
    except:
        print("could not find the link to scroll")
        pass
    try:
        links[i].click()
        time.sleep(generate_delay())
    except:
        try:
            browser.get(website)
            time.sleep(generate_delay())
            links = browser.find_elements_by_class_name('jobtitle')
            links[i].click()
            time.sleep(generate_delay())
        except:
            print("could not click on the link")
            pass
    #print(links[i].text)
    try:
        linked = links[i].text
    except:
        print("could not click on the link")
        linked=np.nan
        pass
    try:
        Date = browser.find_element_by_class_name('date').text
    except:
        print("could not fetch header")
        Date=np.nan
        pass
    try:
        Title = browser.find_element_by_xpath('//*[@id="vjs-header-jobinfo"]').text
    except:
        print("could not fetch header")
        Title=np.nan
        pass
    
    try:
        Company = browser.find_element_by_xpath('//*[@id="vjs-cn"]').text
    except:
        print("could not fetch company")
        Company = np.nan
        pass
        
    try:
        Location = browser.find_element_by_xpath('//*[@id="vjs-loc"]').text
    except:
        print("could not fetch location")
        Location = np.nan
        pass 
    try:
        Details = browser.find_element_by_xpath('//*[@id="vjs-content"]').text
        Details=Details.split('\nil y a ')[0] #on enlève les dates de parution de l'annonce présent dans "Details"
    except:
        print("could not fetch role description")
        Details = np.nan
        pass
    try:
        DetailsLoc = Details+Location+Title
    except:
        print("could not concat")
        DetailsLoc = np.nan
        pass
    url = browser.current_url
    df_indeed.loc[scraping_jobpost.counter]=[Title,Details,linked,Company,Location,estimated,Date,timestamp,DetailsLoc,url]
    df_indeed.to_csv('df_indeed1.csv', index=False, header=True)
    df_counter.loc[thread_id]=[thread_id,count]
    df_counter.to_csv('df_counter.csv', index=False, header=True)
    try:
        if db.new_indeed_hope.find_one({'DetailsLoc': DetailsLoc})==None: #check si Details loc existe déjà dans la base
            #si elle n'existe pas, la ligne est ajoutée
            db.new_indeed_hope.insert_one({"Title":Title,"Details":Details,"linked":linked,"Company":Company,"Location":Location,"estimated":estimated,"Date":Date,"timestamp":timestamp,"DetailsLoc":DetailsLoc,"url":url});
    except:
        print("could not upload data or already there")
    print("counter"+str(scraping_jobpost.counter))
    #df_indeed.loc[thread_number]=[Title,Details]
    scraping_jobpost.counter += 1 





#Cette fonction va permettre de lancer plusieurs Thread. Elle prend thread id en argument.
def f(thread_id):    
    browser = webdriver.Firefox()  #attente que l'instance selenium s'ouvre
    browser.get('https://www.indeed.fr/')#va sur Indeed
    browser.maximize_window()#Mode plein écran
    print(thread_id)
    pagination.counter = 0  #nombre de fois que la fonction pagination a tourné
    scraping_jobpost.counter = 0  #nombre de fois que la fonction scrapping a tourné
    df_counter = pd.DataFrame({'thread' : [],'Page_count' : []})
    count=0  #ce compteur permettra de changer la ville après 90 pages. Il permet aussi de savoir quel est le compte de page.
    choice = random.choice(city)#choice prend un le nom d'une ville dans la liste de villes 
    city.remove(choice)# efface la ville selectionnée de la liste
    
    pages2 = "&start="+str(count)+"0"
    website = "https://www.indeed.fr/emplois?q="+str(keyword)+str(estimated)+"&l="+str(choice)+str(pages2)
    randomize_click(choice,count,website,browser,keywords,skills,thread_id)

threads = []
for i in range(5):
    t = threading.Thread(target=f, args=(i,))
    threads.append(t)
    t.start()



