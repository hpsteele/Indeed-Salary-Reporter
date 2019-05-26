#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 14:12:31 2019
@author: Celia
"""


#On lance la prédiction Random Forrest
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

print("random forrest...")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

import matplotlib.pyplot as plt

# ######Pour remplir les nans de la colonne experience on va mettre la moyenne de chaque categorie "seniority"######

 
annonces = pd.read_csv('df_pymongo_new.csv',encoding='utf-8')#On elimine les nan
annonces=annonces.dropna(subset=['true_date'])#On elimine les nan
annonces=annonces.dropna(subset=['Details'])#On elimine les nan
annonces.Bassin_emploi[annonces.Bassin_emploi.isnull()]="Paris"

#je remplace les valeurs Niveau d'étude manquants par la moyenne de la ville
for i in annonces["Bassin_emploi"].unique():
    annonces["Niveau d'études"].loc[annonces["Bassin_emploi"]==i] = annonces["Niveau d'études"].fillna(annonces["Niveau d'études"].loc[annonces["Bassin_emploi"]==i].mean())

#j'efface les colonnes inutiles 
annonces = annonces.drop(["index","Capital","Chiffre","Company","Date","Details","lang","Title","Location","true_date","url","timestamp","New/vs/Old","Seniority","position","Contrat","Langages",'Big_data_opensource', 'domain', 'Cloud_providers', 'Big_data_providers', 'poss_cols', 'poss_cols2', 'poss_cols3','all_skills','Activité', 'Activité2','nez','dupli','info'],axis=1)

annonces2 = annonces.loc[annonces['Salaires'].notnull()]


#Je défini X et Y et j'enlève les annonces Salaires de X 
X = annonces2.drop(["Salaires"],axis=1)
y = annonces2.Salaires

#je one hot encode X.
X=pd.get_dummies(X)
X=X.drop(["Seniority_simplified_mid"],axis=1)

#je split entre train et test. 
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 0)

#initialise the regressor
regressor = RandomForestRegressor(n_estimators=300, min_samples_split=2)
regressor.fit(X_train, y_train)

#predict
y_pred = regressor.predict(X_test)

###HOW TO EVALUATE this?
from sklearn import metrics
print("r2_score random forrest")
print(metrics.r2_score(y_test, y_pred))#
print("mean_absolute_error")
print(metrics.mean_absolute_error(y_test, y_pred))#
print("mean_squared_error")
print(metrics.mean_squared_error(y_test, y_pred))#
print("median_absolute_error")
print(metrics.median_absolute_error(y_test, y_pred))#
print("explained_variance_score")
print(metrics.explained_variance_score(y_test, y_pred))#


#On lance la prédiction SVM
print("svm...")

from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
#df = pd.read_csv('C:/Users/Administrateur/Documents/SIMPLONr/df_pymongo_merged_with_companies.csv',encoding='utf-8')
import matplotlib.pyplot as plt
annonces = pd.read_csv('df_pymongo_new',encoding='utf-8') #On retelecharge le dataset 
annonces=annonces.dropna(subset=['true_date'])#On elimine les nan
annonces=annonces.dropna(subset=['Details'])#On elimine les nan
annonces.Bassin_emploi[annonces.Bassin_emploi.isnull()]="Paris"

#on remplace les missing values de niveau d'étude par la ville 
for i in annonces["Bassin_emploi"].unique():
    annonces["Niveau d'études"].loc[annonces["Bassin_emploi"]==i] = annonces["Niveau d'études"].fillna(annonces["Niveau d'études"].loc[annonces["Bassin_emploi"]==i].mean())

#je remplace les valeurs Niveau d'études manquants par la moyenne de la ville
annonces = annonces.drop(["index","Capital","Chiffre","Company","Date","Details","lang","Title","Location","true_date","url","timestamp","New/vs/Old","Seniority","position","Contrat","Langages",'Big_data_opensource', 'domain', 'Cloud_providers', 'Big_data_providers', 'poss_cols', 'poss_cols2', 'poss_cols3','all_skills','Activité', 'Activité2','nez','dupli','info'],axis=1)

#je ne prends que les valeurs qui ont un Salaire
annonces2 = annonces.loc[annonces['Salaires'].notnull()]

#je défini les valeurs X et y
X = annonces2.drop(["Salaires"],axis=1)
y = annonces2.Salaires.astype(int)

#je one hot encode 
X=pd.get_dummies(X)

#je standardise les données
sc = StandardScaler()
X=X.drop(["Seniority_simplified_mid"],axis=1)
X = sc.fit_transform(X)



#je divise le test et le train 
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 0)

#initialise the classifier
from sklearn.svm import SVC
classifier = SVC(kernel = 'linear', random_state = 0)
classifier.fit(X_train, y_train)

#predict
y_pred = classifier.predict(X_test)

###HOW TO EVALUATE DIS?
from sklearn import metrics
print("r2_score svm")
print(metrics.r2_score(y_test, y_pred=
print("mean_absolute_error")
print(metrics.mean_absolute_error(y_test, y_pred))
print("mean_squared_error")
print(metrics.mean_squared_error(y_test, y_pred))
print("median_absolute_error")
print(metrics.median_absolute_error(y_test, y_pred))
print("explained_variance_score")
print(metrics.explained_variance_score(y_test, y_pred))




#create a list of predictions : #reprend le fichier complet sans les salaires, auquels on applique le même traitement que les fichiers initiaux. 
annonces=annonces.drop(["Salaires"],axis=1)
annonces=pd.get_dummies(annonces)
annonces=annonces.drop(["Bassin_emploi_île de france","Seniority_simplified_mid"],axis=1) 
salaire_forest = regressor.predict(annonces)  #on applique l'algo de prédiction sur le dataset obtenu avec random forrest 


salaire_svm = classifier.predict(annonces)#on applique l'algo de prédiction sur le dataset obtenu avec svm
#add the predictions


#re import the dataset 
original = pd.read_csv("C:/Users/Administrateur/Documents/SIMPLONr/df_pymongo_new.csv", encoding = 'utf8')
original=original.dropna(subset=['true_date'])#On elimine les nan
original=original.dropna(subset=['Details'])#On elimine les nan
#add the predictions
original['salaire_forest'] = salaire_forest ##On créé la colonne salaire_forest 
original['salaire_svm'] = salaire_svm #On créé la colonne salaire_svm 




#export to csv
original.to_csv('df_pymongo_merged_preds.csv',encoding='utf8')

