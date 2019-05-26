import pymongo
import pandas as pd
from pymongo import MongoClient
client = MongoClient()
db = client.new_indeed_raw
collection = db.new_indeed_hope
data = pd.DataFrame(list(collection.find()))

print("preprocessing")

#on prends seulement les colonnes pertinentes
data = data.loc[9:]#on prends seulement les colonnes pertinentes
data = data.reset_index() #on reset l'index
data = data.drop(["DetailsLoc"],axis=1) #efface la colonne  DetailsLoc, qui ne servait qu'à checker les doublons pendant le scrapping
data.to_csv('df_new_pymongo_no_duplicate.csv', index=False, header=True)



# Importation des librairies
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt

# Préparation de la visualisation
plt.rcParams['figure.figsize'] = (15, 3)
plt.rcParams['font.family'] = 'sans-serif'

# Importation du dataframe
annonces = pd.read_csv('df_new_pymongo_no_duplicate.csv',encoding='utf-8')

# Suppression de colonnes inutiles
annonces.drop(['index','estimated','linked','_id'], axis=1, inplace=True)

annonces = annonces.drop(annonces.index[8])#empty line
annonces = annonces.reset_index()

annonces = annonces[annonces["timestamp"].notna()]
annonces["timestamp"] = pd.to_datetime(annonces["timestamp"],infer_datetime_format=True)
annonces = annonces.reset_index()

# Fonction vraie_date - Une fonction qui donne la vraie date de publication
# d'une offre d'emploi en prenant une ligne d'un df dont la
# colonne "Date" est en forme "Il y a..." et qui a une colonne "timestamp"
# Entrées: pd.DataFrame df
# Actions: Rien
# Sorties: pd.Series - une colonne avec le même nombre de lignes que df
def vraie_date(df):
    
    # Première fonction pour trouver l'unité de temps après "il y a"
    unit_dic = {"heure": "h", "jour":"D", "mois":"D", "minute":"m", "second":"second"}
    def unit_giver(jobby):
        temp = jobby
        for scale in unit_dic.keys():
            if scale in temp:
                temp = unit_dic[scale]
        return temp

    # Petite fonction pour enlever les symboles '+'
    def plus_remover(jobby):
        temp = jobby
        if "+" in temp:
            temp = temp[:-1]
        return pd.to_numeric(temp, errors='coerce')

    # Crée un tuple contenant les sorties des fonctions au-dessus pour
    # une ligne du dataset
    def time_diff(jobby):
        if "mois" not in jobby[1]:
            return plus_remover(jobby[0]), unit_giver(jobby[1])
        return 30*plus_remover(jobby[0]), unit_giver(jobby[1])
    
    return df["timestamp"] - df["Date"].apply(lambda x: time_diff(x[7:].split(" "))).apply(lambda x: pd.to_timedelta(x[0], unit=x[1]))

# On passe créé un nouveau feature pour détecter les offres "fraiches " (celle postées ds la semaine)
annonces["true_date"]=vraie_date(annonces)

import time
import datetime
#Ensuite on créé une colonne old/vs/new, pour identifier les offres fraiches de la semaine
date_now = datetime.datetime.now()
annonces["New/vs/Old"]=np.nan
annonces["New/vs/Old"].loc[date_now-annonces.true_date>pd.Timedelta(7,'D')]="Old"
annonces["New/vs/Old"].loc[annonces["New/vs/Old"].isnull()]="New"


# On passe les colonnes interessantes en minuscules pour faciliter les regex
annonces['Title'] = annonces['Title'].str.lower() 
annonces['Details'] = annonces['Details'].str.lower()


# Data preprocessing : Type de poste

# on déclare une liste de mots clés pour recherche la seniorité dans type de poste dans annonces
type_poste =["leader","lead","directeur","directrice","manager","vp","svp","president","pdg","senior","director","cto","chief","general manager","comex","evp","executive","responsable région","chef","membre","board","head","graduate","junior"]

# on appelle str.extract qui va se charger de reconnaitre les items de la liste
annonces['Seniority'] = annonces['Title'].str.extract("(" + "|".join(type_poste) +")", expand=False)

executives =["chef","comex","senior",'cto','direction', 'executive','director',"manager","comex",'directeur',"directrice","leader","lead", 'head', 'chief','responsable région','vp',"evp","chief","general manager","president","pdg","member"]
junior =["junior",'graduate','stage','intern','internship','assistant','student']

# Seniority simplified va être principalement utilisé pour des plots car il est colinéaire avec seniority
annonces['Seniority_simplified']=annonces['Title'].str.extract("(" + "|".join(executives) +")", expand=False)
annonces['Seniority_simplified']=annonces['Seniority_simplified'].replace(executives,"executives")
annonces['Seniority_simplified'].loc[annonces['Seniority_simplified'].isnull()]=annonces['Title'].loc[annonces['Seniority_simplified'].isnull()].str.extract("(" + "|".join(junior) +")", expand=False)
annonces['Seniority_simplified']=annonces['Seniority_simplified'].replace(junior,"junior")

#Création de la variable des postes :#DEFINITION DU RÔLE  data scientist/ vs analyste etc. 
#On selectionne par mot clié d'abord sur le titre. 
#on remplace étape par étape "par élimination". Si la colonne est vide, alors elle reçoit le traitement de la ligne suivante 

#On commence par le titre, puis par le details (mais les mots clés seront "plus forts" pour details)

#Création des listes de postes analyste, scientist,bi,dev,architect
analyst = ["analyste","analyst","analytics","analyst","quantitative","quant ","économiste","economist","consultant","consulting"]
scientist = ["scientist","sciences","science","scientifique","scien","math","économiste","statisticien","statistique","r&d","chercheur","machine learning","deep learning"," ml ",]
Business_Intelligence = ["businessintelligence","business intelligence"," bi "]
Developpeur = ["developpeur","devops","ingénieur","développeyur","software","développement","java","engineer","ingenieur","développeur","dev ","codeur","intégrateur"]
IT_architect = ["cloud","dba","sql","informatique","infrastructure","architecte","architect","intégrateur","architect","database","data base","base de donnée","base de données"]
other_data = ["data","données","donnee","donnees"]

#Création d'une colonne spécifique extractant info des titres basé sur les listes de postes
annonces["position"]=annonces['Title'].str.extract("(" + "|".join(analyst) +")")
annonces["position"]=annonces["position"].replace(analyst,"analyst")
annonces["position"].loc[annonces["position"].isnull()]=annonces['Title'].loc[annonces["position"].isnull()].str.extract("(" + "|".join(scientist) +")", expand=False)
annonces["position"]=annonces["position"].replace(scientist,"scientist")
annonces["position"].loc[annonces["position"].isnull()]=annonces['Title'].loc[annonces["position"].isnull()].str.extract("(" + "|".join(Business_Intelligence) +")", expand=False)
annonces["position"]=annonces["position"].replace(Business_Intelligence,"Business_Intelligence")
annonces["position"].loc[annonces["position"].isnull()]=annonces['Title'].loc[annonces["position"].isnull()].str.extract("(" + "|".join(Developpeur) +")", expand=False)
annonces["position"]=annonces["position"].replace(Developpeur,"Developpeur")
annonces["position"].loc[annonces["position"].isnull()]=annonces['Title'].loc[annonces["position"].isnull()].str.extract("(" + "|".join(IT_architect) +")", expand=False)
annonces["position"]=annonces["position"].replace(IT_architect,"IT_architect")
annonces["position"].loc[annonces["position"].isnull()]=annonces['Title'].loc[annonces["position"].isnull()].str.extract("(" + "|".join(other_data) +")", expand=False)
annonces["position"]=annonces["position"].replace(other_data,"other_data")


#recréation de nouvelles listes pour extraire info des details lorsque le titre était insuffisant. "bi" serait inadapté pour l'extraction dans la colonne details
analyst = ["analyste","analyst","analytics","analyst"]
scientist = ["scientist","scientifique","math","statisticien","machine learning","tensorflow","réseaux de neuronnes","deep learning","clustering","reinforcement learning","nlp","natural langage","modélisation","modeling","predict"]
Business_Intelligence = ["businessintelligence","business intelligence"]
Developpeur = ["developpeur","devops","ingénieur","développeyur","engineer","ingenieur","développeur"]

##Completion d'une colonne spécifique extractant info des details basé sur les nouvelles listes de postes
annonces["position"].loc[annonces["position"].isnull()]=annonces['Details'].loc[annonces["position"].isnull()].str.extract("(" + "|".join(analyst) +")", expand=False)
annonces["position"]=annonces["position"].replace(analyst,"analyst")
annonces["position"].loc[annonces["position"].isnull()]=annonces['Details'].loc[annonces["position"].isnull()].str.extract("(" + "|".join(scientist) +")", expand=False)
annonces["position"]=annonces["position"].replace(scientist,"scientist")
annonces["position"].loc[annonces["position"].isnull()]=annonces['Details'].loc[annonces["position"].isnull()].str.extract("(" + "|".join(Business_Intelligence) +")", expand=False)
annonces["position"]=annonces["position"].replace(Business_Intelligence,"Business_Intelligence")
annonces["position"].loc[annonces["position"].isnull()]=annonces['Details'].loc[annonces["position"].isnull()].str.extract("(" + "|".join(Developpeur) +")", expand=False)
annonces["position"]=annonces["position"].replace(Developpeur,"Developpeur")


#EXPERIENCE : ici, on va prendre toutes les mentions d'un certain nombre d'année entre 0 et 10 ans
# Data preprocessing : Expérience /

# Nouvelle colonne 'Experience' à partir de 'Details'
annonces['Experience'] = annonces['Details'] 

# On extrait les 'expériences' en 'expérience' selon différentes syntaxes possibles
annonces['Experience'] = annonces['Experience'].str.replace("expérience","experience").replace("expériences","experience").replace("d'expérience","experience").replace("d'expériences","experience").replace("experiences","experience")
annonces['Experience'] = annonces['Experience'].str.replace("several","2").replace("plusieurs","2").replace("dizaine","10").replace("plusieurs années","2").replace("several years","2")
annonces['Experience'] = annonces['Experience'].str.replace("customer experience","").replace("online experience","").replace("user experience","")

# On remplace les durées en lettres par des digits
annonces['Experience'] = annonces['Experience'].str.replace("une","1").replace("un","1").replace("one","1").replace("deux","2").replace("trois","3").replace("quatre","4").replace("cinq","5").replace("six","6").replace("sept","7").replace("huit","8").replace("neuf","9").replace("dix","10").replace("quinze","15")
annonces['Experience'] = annonces['Experience'].str.replace("two","2").replace("three","3").replace("four","4").replace("five","5").replace("six","6").replace("seven","7").replace("eight","8").replace("nine","9").replace("ten","10").replace("fifteen","15")

#  Regex pour prendre tous les digits avant 'year/years/ans/an ...'
tmp = annonces['Experience'].str.extractall("([0-9]+)(?=\s(an |ans |année |années |years |year |ans\r\n|années\r\n|année\r\n|an\r\n|year\r\n|years\r\n|ans,|année,|an,|années,|years,|year;|years;|ans;|an;|année;|années;|year.|years.|ans.|an.|année.|années.))")
tmp[0]=tmp[0].astype("float")
# On elimine les valeurs suppérieures à 10 (hypothèse : les employeurs ne prennent pas plus de 11 ans d'expérience)
tmp[0]=tmp[0].loc[tmp[0]<11]  
tmp=tmp.groupby(level=0).max() #on garde la valeur maximum ()
annonces['Experience'] = tmp.groupby(tmp.index.get_level_values(0)).agg(list) #on réinsere les groupes dans le dataframe
annonces['Experience']=annonces['Experience'].astype(str).str.replace('\[|\]|\'', '') #on enleve les crochets

#Ensuite, on va compléter l'expérience où les valaurs sont manquantes en ajoutant "0" là où les entreprises recherchent un stagiaire ou une alternance

#je créé une classe mid entre junior et senior 
annonces["Seniority_simplified"]=annonces["Seniority_simplified"].fillna("mid")
#je remplace les valeurs nulles de expérience par la valeur "executuve","junior","mid"
annonces["Experience"].loc[annonces["Experience"].isnull()]=annonces['Seniority_simplified'].loc[annonces["Experience"].isnull()]
#je remplace les valeurs nulles de junior par "0"
annonces["Experience"].loc[annonces["Experience"]=="junior"]=annonces["Experience"].loc[annonces["Experience"]=="junior"].str.replace("junior","0")
#je remplace les valeurs excutives et mid par des nan
annonces["Experience"]=annonces["Experience"].replace(r'executives|mid', np.nan, regex=True)
#je remets les string en floats
annonces["Experience"]=annonces["Experience"].astype(float)

#On arrive à 25% de valeurs manquantes/.je remplace les valeurs manquantes de l'expérience par la moyenne des de l'XP par la seniority simplified
for i in annonces["Seniority_simplified"].unique():
    annonces["Experience"].loc[annonces["Seniority_simplified"]==i] = annonces["Experience"].fillna(annonces["Experience"].loc[annonces["Seniority_simplified"]==i].mean())

#on converti les string en nan ou float
def replace(l):
    """Cette fonction prends en paramètres une liste ou series qui est composé de strings (soit 'nan' ou un nombre ex. '5.0')
    il retourne une liste avec soit des nans ou des floats
    on peut ajouter ensuite cette liste à notre dataframe"""
    l2 = [0 for x in range(len(l))]
    for i in range(len(l)):
        elt = l[i]
        if elt == 'nan':
            l2[i] = np.nan
        else:
            l2[i] = float(elt)
    return l2
#on applique au dataset 
annonces['Experience'] = replace(annonces['Experience'])
#type(annonces['Experience'][2]) #pour verifier que la fonction a fonctionnée - doit retourner un nan 

# Fonction prem_exp - Une fonction qui peut aider à remplir la colonne "Experience".
# Entrées: pd.DataFrame df
# Actions: Rien
# Sorties: pd.Series temp - une series avec le même index que df, dont les valeurs sont 1 si la colonne "Details" de df
# contient "première" ou "first experience", ou 0 sinon.
def prem_exp(df):
    vrai = (df["Details"].str.contains("première", regex=True)) | (df["Details"].str.contains("first experience", regex=True))
    temp = pd.Series(np.nan, df.index)
    temp.loc[vrai] = 1
    return temp

annonces["prem_exp"] = prem_exp(annonces)
annonces["Experience"] = np.nanmax(annonces[["prem_exp", "Experience"]], axis=1)
annonces = annonces.drop(columns=["prem_exp"])



## Data preprocessing : Type de poste
## on déclare une liste de mots clés pour recherche le type de poste dans annonces
#type_poste =["directeur","directrice","manager","vp","svp","president","pdg","director","cto","chief","general manager","evp","executive","responsable région","chef","membre","board","direction","head","graduate","junior"]
## on appelle str.extract qui va se charger de reconnaitre les items de la liste
#annonces['Seniority'] = annonces['Title'].str.extract("(" + "|".join(type_poste) +")", expand=False)




# Data preprocessing : Contrats

# on cherche les contrats dans ces colonnes avec une regex
# et on remplit une liste de contrats pour chaque annonce

def type_de_contrat(df):
    liste_contrats = []
    regex = r'(?:independent|contracts|contract|interim|internship|intership|permanent|short-term|short term|full-time|part-time|part time|full time|student|student job|student jobs|cdi|cdd|stage|alternance|apprentissage|professionnalisation|freelance|indépendant|independant)'
    for i in range(len(df)):
        l = re.findall(regex,str(df['Title' and 'Details'][i]))
        l = list(set(l))
        liste_contrats.append(l)
    return(liste_contrats)

# on appelle la fonction qui extrait les contrats
c = type_de_contrat(annonces)
# on remplit une colonne 'Contrat' au propre dans le dataframe
c = np.array(c)
annonces["Contrat"] = c

#Replacing missing values in contract with CDI
annonces["Contrat"].loc[annonces["Contrat"]==""]="cdi"

#On définit des colonnes directly one hot encoded pour faciliter les traitement
liste = ['internship','intership',"intern",'student','stage','permanent','full-time','cdi',"durée indeterminée",'contracts','contract','interim','short-term' ,"durée determinée", 'short term' ,'cdd''independent','interim','indépendant','independant',"freelance","freelancing"'student','alternance','apprentissage','professionnalisation','alternant']
stage = ['internship','intership',"intern",'student','stage']
cdi = ['permanent','full-time','cdi',"durée indeterminée"]
cdd = ['contracts','contract','interim','short-term' ,"durée determinée", 'short term' ,'cdd']
freelance = ['independent','interim','indépendant','independant',"freelance","freelancing"]
alternance = ['student','alternance','apprentissage','professionnalisation','alternant']


annonces["stage"]=annonces['Details'].str.extract("(" + "|".join(stage) +")")
annonces["stage"]=annonces["stage"].replace(stage,"1")
annonces["stage"]=annonces["stage"].fillna(0)
annonces["cdi"]=annonces['Details'].str.extract("(" + "|".join(cdi) +")")
annonces["cdi"]=annonces["cdi"].replace(cdi,"1")
annonces["cdi"]=annonces["cdi"].fillna(0)
annonces["cdd"]=annonces['Details'].str.extract("(" + "|".join(cdd) +")")
annonces["cdd"]=annonces["cdd"].replace(cdd,"1")
annonces["cdd"]=annonces["cdd"].fillna(0)
annonces["freelance"]=annonces['Details'].str.extract("(" + "|".join(freelance) +")")
annonces["freelance"]=annonces["freelance"].replace(freelance,"1")
annonces["freelance"]=annonces["freelance"].fillna(0)
annonces["alternance"]=annonces['Details'].str.extract("(" + "|".join(alternance) +")")
annonces["alternance"]=annonces["alternance"].replace(alternance,"1")
annonces["alternance"]=annonces["alternance"].fillna(0)


# Data preprocessing : Salaires

# On nettoie les salaires et on remplace les valeurs vides par des nan
def cleansal(liste):
    for i in range(len(liste)):
        if len(liste[i])==0:
            liste[i] = np.nan
        else:
            liste[i] = liste[i][0]
    return liste

def trouver_salaires(df, colonne):
# on trouve des salaires dans 'colonne' et dans le dataframe entrés en paramètres
# 'colonne' doit etre une string sur laquelle on applique la regex
# on renvoie une liste 
    s = []
    regex = r'((?:Rémunération|Gratification|Salaire|Salary)?\s?:?\s?[0-9]*(?:.|,)[0-9]*(?:.|,)[0-9]*€?\s(?:(?:to|-|à)?\s?[0-9]*(?:.|,)[0-9]*(?:.|,)[0-9]*€?\s)?\s?(?:\/|par|per)\s?(?:mois|an|year|month) )'
    for i in range(len(df)):
        l = re.findall(regex,str(df[colonne][i]))
        s.append(l)
    s = cleansal(s) #on nettoie avec la fonction cleansal 
    return(s)
    
def intify_etc(sals):
    """ sals : liste de salaires en forme de string
    cette fonction convertie toutes les phrases en int's: 
    remplace les salaires avec une moyenne si c'est une fourchette
    et avec une moyenne transformé en annuel s'il sagit d'une salaire par mois
    retourne une liste nettoyée, prête à être ajoutée au dataframe :)) 
    """
    regex = '[0-9]*? ?[0-9]{3}'
    #for each line
    for i in range(len(sals)):
        #if it's not a nan
        if type(sals[i]) != float:
            #now we must separate per months from per year 
            #and fourchettes from non fourchettes
            if 'par an' in sals[i]:
                #print('par an')
                if '-' in sals[i]:
                    #print('fourchette')
                    frm = re.findall(regex,sals[i])[0]
                    to = re.findall(regex,sals[i])[1]
                    frm, to = frm.replace(' ',''), to.replace(' ','')#getting rid of space
                    frm, to = int(frm), int(to)#convert to int 
                    avg = (frm+to)/2 #calculate average
                    sals[i] = avg
                    if sals[i]>200000:
                        sals[i]=sals[i]/12#au cas où, les salaires sont anormalement élévés, on divise par 12
                        
                else:
                    #print('not fourchette')
                    try:
                        sal = re.findall(regex,sals[i])[0]
                        sal=sal.replace(' ','')#get rid of space
                        sals[i] = int(sal)#convert to int
                        if sals[i]>200000:
                            sals[i]=sals[i]/12#au cas où, les salaires sont anormalement élévés, on divise par 12
                    except:
                        print("WARNING "+str(sals[i]))
                        sals[i]=np.nan
            elif 'par mois' in sals[i]:
                #print('par mois')
                if '-' in sals[i]:
                    #print('fourchette')
                    frm = re.findall(regex,sals[i])[0]
                    to = re.findall(regex,sals[i])[1]
                    frm, to = frm.replace(' ',''), to.replace(' ','')#get rid of the space
                    frm, to = int(frm), int(to)#converting to int
                    avg = (frm+to)/2#calculate average
                    par_an = avg*12#convert to yearly salary
                    sals[i] = par_an
                    if sals[i]>200000:
                        sals[i]=sals[i]/12#au cas où, les salaires sont anormalement élévés, on divise par 12
                else:
                    #print('not fourchette')
                    try:
                        sal = re.findall(regex,sals[i])[0]
                        sal=sal.replace(' ','')#get rid of space
                        sals[i] = int(sal)*12#convert to yearly salary
                        if sals[i]>200000:
                            sals[i]=sals[i]/12 #au cas où, les salaires sont anormalement élévés, on divise par 12
                    except:
                        print("WARNING "+str(sals[i]))
                        sals[i]=np.nan
                    #print('not fourchette')
        elif type(sals[i]) == str:
            sals[i] = np.nan
    return sals

# on extrait les salaires 
s = intify_etc(trouver_salaires(annonces, 'Title'))
# on les ajoute dans une nouvelle colonne
annonces['Salaires'] = s


# Data preprocessing : Niveau d'études (on arrive à environ 70% de niveau d'étude captés)

# ajouter une colonne niveau_etude. La fonction niveau d'étude permet de capter tous les doctorats/masters spécialisés etc. Elle transforme tout en bac+quelque chose. 
#Elle capte les "bac + quelque chose "" et ne conserve que la valeur la valeur la plus élevée

def niveau_etudes(df):
    # z est la regex pour extraire Bac+.., bac +..., Master
    # qu'on va chercher dans la colonne Details
    etude=[]
    z = re.compile(r'bac ?\+ ?\d?\/?\d?|master')
    
    for i in range(len(df)):
        bac = re.findall(z,str(df['Details'][i]))
        bac = list(set(bac))
        etude.append(bac)
    return(etude)

# on remplace les mots doctorats etc avec bac+8
annonces["Details"]=annonces["Details"].str.replace(" thèse","bac+8").str.replace("doctorat","bac+8").str.replace("doctorant","bac+8").str.replace("phd","bac+8").str.replace("docteur","bac+8").str.replace("ingenieur","bac+5").str.replace("grande ecole","bac+5").str.replace("grande école","bac+8").str.replace("ingénieur","bac+8").str.replace("école","bac+5").str.replace("ecole","bac+5").str.replace("m2","bac+5").str.replace("m1","bac+5").str.replace("school","bac+5").str.replace("degree","bac+5").str.replace("bachelor","bac+3").str.replace("licence","bac+3").str.replace("bac+6","bac+5").str.replace("bac+6","bac+5").str.replace("M.Sc","bac+5").str.replace("Ph.D","bac+8").str.replace("degree","bac+8")     
# on appelle la fonction qui traite le niveau d'études
annonces["Niveau d'études"] = niveau_etudes(annonces)
# on clean la colonne niveau d'étude
annonces["Niveau d'études"]=annonces["Niveau d'études"].astype(str).str.replace("master","5").replace("bac","").replace("+","")
listetude = ["1","2","3","4","5","6","7","8"]
# on extrait les niveau d'étude maximal
multi_index_study = annonces["Niveau d'études"].astype(str).str.extractall("(" + "|".join(listetude) +")")
annonces["Niveau d'études"]=multi_index_study.groupby(level=0).max()



# Data preprocessing : Location

# le code ci-dessous permet de déterminer le bassin d'emploi en se basant sur le mot clé recherché
annonces['Bassin_emploi'] = annonces['Location'] #création de la colonne bassin d'emploi
# extraction de mot clé utilisé pour la recherche
annonces['Bassin_emploi'] = annonces['url'].str.extract("(?<=&l=)(.*)(?=&start)", expand=False)
# reformater île de France 
annonces['Bassin_emploi'] = annonces['Bassin_emploi'].replace("%C3%AEle%20de%20france","île de france")

# le code permet une nouvelle variable appellée inner_city
annonces['Location'] = annonces['Location'].str.lower()#reformater la colonne location en minuscule 
Inner_City = ["75","bordeaux","paris","nantes","toulouse","lyon"]#definir liste de valeur qui sont théoriquement dans la ville même
annonces['Inner_City'] = annonces['Location'].str.extract("(" + "|".join(Inner_City) +")", expand=False) #extrait les valeurs en centre villes 
annonces['Inner_City'] = annonces['Inner_City'].replace(Inner_City,"Inner_City")#remplace les valeurs en centre villes
annonces['Inner_City'] = annonces['Inner_City'].notnull()
annonces['Inner_City'] *= 1

### Cette fonction permet de detecter la langue de l'offre (fr, not fr)
##
from langdetect import detect # import langdetect
##
def try_detect(cell):# fonction pour detecter la langue
    try:
        detected_lang = detect(cell)
    except:
        detected_lang = None 
    return detected_lang

## ça a pris 3 minutes pour 7000 lignes
annonces['langage'] = annonces["Details"].apply(try_detect) # applique la fonction 
annonces['langage'].loc[annonces['langage']=="fr"].count()  #nombre d'offre en français
##
###binarize en fr et non fr
annonces['langage'] = annonces['langage'].loc[annonces['langage']=="fr"] 
annonces['langage'] = annonces['langage'].notnull()
annonces['langage'] *= 1

# Data preprocessing : Compétences 

# on extrait les compétences spécifiques avec une regex
def langages_pro(df):
    # on cherche dans la colonne 'Details'
    langage=[]
    regex = r'(english|anglais|espagnol|german|allemand|bilingue|trilingue|spanish)'
    
    for i in range(0, len(df)):
        L = re.findall(regex,str(df['Details'][i]))
        L = list(set(L))
        langage.append(L)
    return(langage)

annonces["Langages"] = langages_pro(annonces)


#On transforme les skills (appellées ici langage) en one hot encoded 
annonces['Langages']=annonces['Langages'].astype(str).str.replace('\[|\]|\'', '')
annonces['Langages']=annonces['Langages'].str.replace(' ', '')
annonces= pd.concat([annonces, annonces.Langages.str.get_dummies(sep=',')], axis=1)

#Les lises ci dessous permettront de regrouper les termes similaires (examples :ml et machine learning)
#r = ["shiny", "rshiny", "rstudio","r studio",",r "," r,"]
#python = ["pandas","sk learn","sklearn","sci-kit","numpy","sk learn","sci-kit","scikit","sklearn"]
#statistique = ["stats","statistics","statistique","statistiques"]
#machine_learning = ["machinelearning"",machine learning","ml"]
#nlp = ["natural language","nlp","nlu"]
#chatbot = ["chatbot","chatbots"] 
#annonces.Details=annonces.Details.replace(python,"python")
#annonces.Details=annonces.Details.replace(statistique,"statistique")
#annonces.Details=annonces.Details.replace(machine_learning,"machine_learning")
#annonces.Details=annonces.Details.replace(nlp,"nlp")

#remplacement des occurences de r  
annonces.Details=annonces.Details.str.replace(",r "," r ").replace(" r,"," r ").replace(" r."," r ").replace(" r;"," r ").replace("rstudio"," r ").replace("rshiny"," r ")



languages2 = [" r ","power query","unix","linux","json","golang","golearn","deap ","maple","julia","python"," sql",",sql","nosql","git ","matlab","c\+\+?","scala","ruby","php","vba","javascript","java ","d3","sci-kit","scikit","keras","tensorflow","pytorch","pandas","numpy"," excel ","powerpoint","plotly","dash ","sas","spss","sk learn","ggplot2","rshiny","shiny","jupyter","networkx","selenium","beautifulsoup","rstudio","auto ml","c\+","tpot","sas","perl"] 
              
Big_data_providers = ["cloudera","aws","amazon","impala","dataiku","zeppelin","graffana","tableau","qlik","spotfire","jira","confluence","bamboo","jenkins","ansible","tableau","power-bi","powerbi","power bi","bigstep","denodo","informatica","azure","koverse","oracle","sap","platfora","zaloni","collibra","alation","mapr"," dataiku ","podium data","zeenea","ecl","flare","google visualization","tamr","saagie","zoomdata","looker","jethro","datameer","atscale","teradata","presto","vectorh","bigsql","datanami","dremio","olap cube","alteryx","birst","datawatch","domo","gooddata","looker","pyramidAnalytics","zoomdata","datawrapper","dwaas","redshift","bedrock","blazingdb ","druid","clickHouse","google big query","oryx","h20","photon ml","prediction.io","seldon","shogun","weka","algorithmia","algorithms.io","amazon ml","bigml"," dataRobot","fico","google prediction","haven ondemand","watson","plyrmr","mathmorks","beyondcore","bime","clearstory"," domo ","gooddata","inetsoft","infocaptor"," logi analytics","microstrategy","rpognoz"," lumira","kafka","esri ","sisense","spotfire","thoughtspot","yellowfin","databricks","datarobot","machine learning studio","purepredictive","predicsis","yottamine","ibm db2","infoworks","heka ","logstash ","kestrel","flume ","flink ","nfs","insightedge","streamanalytix","streamlio","streamsets","streamtools","talend","infoworks","insightedge","kx data","lightBend","heron"] 

Big_data_opensource= ["ubuntu","hive","spark","hadoop","spark","mongodb","mongodb","apache", "mapreduce", "hadoop", "hdfs","cassandra", "hbase","ElasticSearch","neo4j", "mysql","github","gitlab","bitbucket","kibana", "ngrox", "StackOverflow","hortonworks","HBase", "couchdb", "postgres", "mammothdb","mariadb"] 

domain = ["dashboard"," de bord","data lake","datalake","back-end","front-end"," api","etl","data warehouse","statistics","statistique","physics","physique","predict","reporting","bigstep","réseaux de neurones","full stack"," governance"," Reporting","kpi"," Scripting"," unittest","testing","version control","algorithmie","chatbot"," scraping","scrapping","webscraping","wescrap","webscrapping","graph database","maths"," nlp"," machine learning","ml","deep learning"," Scrum","Kanban","agile"] 

Cloud_providers = ["containers","saas","paas","iaas","baas","datacenter","virtuozzo","docker","tsuru ","kubernetes","activestate","apprenda","centurylink","cloudbees ","platform9 ","cloudify","atomia"," cisco"," metapod","cloudstack"," nutanix","openstack","omnistack"," vmware","zerostack","sddc ","avinetworks ","hyperscale ","dynatrace ","tibco","cloudyn ","engine yards","monitis ","xplenty","talend","moskitos","maestrano","azuqua","apppoint","adeptia","elastic.io","google cloud"," gridgrain","heroku","ibm bluemix","profitbricks","dokku","nginx "," deis","coreos"," ceph","docker","softlayer","digitalocean","joyent","linode"," rackspace","coreos","amazon web services","rancheros","snappy"," RedHat","mesosphere dcos","vmware","containers","openvz ","hypervisor","virtual machines","chroot","vmare","esxcitrix","xenserver","salesforce"] 


#On crée des nouveaux features correspondant au différentes types de skills
multi_index_ = annonces['Details'].str.extractall("(" + "|".join(languages2) +")")
annonces["lang"]=multi_index_.groupby(multi_index_.index.get_level_values(0)).agg(list)

multi_index_ = annonces['Details'].str.extractall("(" + "|".join(Big_data_opensource) +")")
annonces["Big_data_opensource"]=multi_index_.groupby(multi_index_.index.get_level_values(0)).agg(list)

multi_index_ = annonces['Details'].str.extractall("(" + "|".join(domain) +")")
annonces["domain"]=multi_index_.groupby(multi_index_.index.get_level_values(0)).agg(list)

multi_index_ = annonces['Details'].str.extractall("(" + "|".join(Cloud_providers) +")")
annonces["Cloud_providers"]=multi_index_.groupby(multi_index_.index.get_level_values(0)).agg(list)

multi_index_ = annonces['Details'].str.extractall("(" + "|".join(Big_data_providers) +")")
annonces["Big_data_providers"]=multi_index_.groupby(multi_index_.index.get_level_values(0)).agg(list)


all_skills = languages2
all_skills  +=Big_data_providers
all_skills  +=Big_data_providers
all_skills  +=domain
all_skills  +=Cloud_providers

multi_index_ = annonces['Details'].str.extractall("(" + "|".join(all_skills) +")")
annonces["all_skills"]=multi_index_.groupby(multi_index_.index.get_level_values(0)).agg(list)
annonces['all_skills']=annonces['all_skills'].astype(str).str.replace('\[|\]|\'', '')
annonces['all_skills']=annonces['all_skills'].str.replace(' ', '')
annonces= pd.concat([annonces, annonces.all_skills.str.get_dummies(sep=',')], axis=1)

annonces=annonces.drop(["level_0","index"],axis=1)
annonces = annonces.reset_index()



#On enlève les doublons
def single_skills(df):
    listeskills=[]
    for i in range(len(df)):
        #print(type(df[i]))
        if type(df[i])==list:
            l = df[i]
            l = list(set(l))
            listeskills.append(l)
        else:
            l = df[i]
            listeskills.append(l)
    return(listeskills)

#On crée un compte de chaque type de skills. #On créer les feature counts pour essayer de quantifier...
#...le nombre de skills demandées dans une offre pour voire si on peut identifier une corrélation 
annonces["lang"] = single_skills(annonces["lang"])
annonces["Big_data_opensource"]=single_skills(annonces["Big_data_opensource"])
annonces["Cloud_providers"]=single_skills(annonces["Cloud_providers"])
annonces["domain"]=single_skills(annonces["domain"])
annonces["Big_data_providers"]=single_skills(annonces["Big_data_providers"])

#On efface les doublons et on calcule le nombre d'éléments de la liste
def count_skills(df):
    countskills=[]
    for i in range(len(df)):
        if type(df[i])==list:
            l=len(df[i])
            countskills.append(l)
        else:
            l = 0
            countskills.append(l)
    return(countskills)


#On crée un compte de chaque type de skills
annonces["count_lang"]=count_skills(annonces["lang"])
annonces["count_Big_data_opensource"]=count_skills(annonces["Big_data_opensource"])
annonces["count_Cloud_providers"]=count_skills(annonces["Cloud_providers"])
annonces["count_domain"]=count_skills(annonces["domain"])
annonces["count_Big_data_providers"]=count_skills(annonces["Big_data_providers"])




#"FEATURE GENERATION : toujours en developpement  ""
#Bag_of words : not used now
# 10% - 20%
#poss_cols = ["big data", "esprit équipe", "formation bac", "machine learning", "nouvelles technologies"]
#poss_cols += ["sein équipe", "travail équipe"]

# 5% - 10%
#poss_cols2 = ["chef projet", "conception développement", "développement logiciel", "développement web", "expérience significative"]
#poss_cols2 += ["formation supérieure", "html css", "sql server", "test unitaires", "travailler équipe", "veille technologique"]

# 3% - 5%
#poss_cols3 = ["agile scrum", "applications web", 'business intelligence', 'deep learning', 'full stack', 'ecole ingénieur']
#poss_cols3 += ['full stack', 'html5 css3', 'intelligence artificielle', 'solutions innovantes']

# définition de nouveaux champs lexicaux
#leadership = ["comex","strategie","strategy","leadership"]
#investment = ["levée de","levées de"," raises"," raised"]

#multi_index_ = annonces['Details'].str.extractall("(" + "|".join(poss_cols) +")")
#annonces["poss_cols"]=multi_index_.groupby(multi_index_.index.get_level_values(0)).agg(list)

#multi_index_ = annonces['Details'].str.extractall("(" + "|".join(poss_cols2) +")")
#annonces["poss_cols2"]=multi_index_.groupby(multi_index_.index.get_level_values(0)).agg(list)

#multi_index_ = annonces['Details'].str.extractall("(" + "|".join(poss_cols3) +")")
#annonces["poss_cols3"]=multi_index_.groupby(multi_index_.index.get_level_values(0)).agg(list)

#annonces["poss_cols"]=single_skills(annonces["poss_cols"])
#annonces["poss_cols2"]=single_skills(annonces["poss_cols2"])
#annonces["poss_cols3"]=single_skills(annonces["poss_cols3"])



# Correction des salaires outliers (à partir de 200000€ / an) on divise par 12 (déjà fait mais au cas où)
mask = annonces['Salaires'] >= 200000
m = annonces[mask]
print(m)
for i in m.index.values:
    annonces['Salaires'][i] = int(annonces['Salaires'][i]/12)


# enlever crochets dans les colonnes
annonces['Contrat']=annonces['Contrat'].astype(str).str.replace('\[|\]|\'', '')
annonces["Niveau d'études"]=annonces["Niveau d'études"].astype(str).str.replace('\[|\]|\'', '')   
annonces['Langages']=annonces['Langages'].astype(str).str.replace('\[|\]|\'', '')


# Remplacement des valeurs manquantes par la fréquence la plus logique ou la plus haute 
annonces["Seniority"].loc[annonces["Seniority"].isnull()]="not senior"


# il y a quelques doublons à cause d'un changement d'avis. On les enlèves de cette manière
annonces.Title=annonces.Title.str.replace(",","")
annonces['nez']=annonces['Title'].str.extract(r'((?!\d avis)^.*)')
annonces['Details'] = annonces['Details'].str.split('il y a ').str[0]
annonces['Details'] = annonces['Details'].str.replace("\\r","").replace("\\n","")
annonces["dupli"] = annonces['nez']+annonces['Details']+annonces['Location']
annonces=annonces.loc[~annonces.dupli.duplicated()]


#Merging with the file company 
info_corp = pd.read_csv('info_corp.csv',encoding='utf-8')
annonces = pd.merge(annonces, info_corp, on='Company', how='outer')

#Correcting the date columns 
annonces["true_date"] = pd.to_datetime(annonces["true_date"]).dt.date

annonces["Niveau d'études"].loc[annonces["Niveau d'études"]=="nan"]=np.nan #on remplace les strings nan par les nan
annonces=annonces.dropna(subset=['Details']) #on enlève les doublons 
annonces.Bassin_emploi.loc[annonces.Bassin_emploi.isnull()]="Paris" 

##On remplace valeurs manquantes 
for i in annonces["Activité2"].unique():
    annonces["Capital"].loc[annonces["Activité2"]==i] = annonces["Capital"].fillna(annonces["Capital"].loc[annonces["Activité2"]==i].mean())
for i in annonces["Activité2"].unique():
    annonces["Chiffre"].loc[annonces["Activité2"]==i] = annonces["Chiffre"].fillna(annonces["Chiffre"].loc[annonces["Activité2"]==i].mean())
for i in annonces["Bassin_emploi"].unique():
    annonces["Capital"].loc[annonces["Bassin_emploi"]==i] = annonces["Capital"].fillna(annonces["Capital"].loc[annonces["Bassin_emploi"]==i].mean())
for i in annonces["Bassin_emploi"].unique():
    annonces["Chiffre"].loc[annonces["Bassin_emploi"]==i] = annonces["Chiffre"].fillna(annonces["Chiffre"].loc[annonces["Bassin_emploi"]==i].mean())


#Saving to CSV

annonces=annonces.dropna(subset=['timestamp']) #on enlève les nan 
annonces.to_csv('df_pymongo_new.csv', index=False, header=True,encoding="utf-8")
# on plot les salaires
plt.scatter(annonces.index.values,annonces['Salaires'],color='r')
plt.title('Salaire (€ brut/an) ')
plt.xlabel('index')
plt.ylabel('Salaire')
plt.show()

