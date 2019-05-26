import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import datetime
from matplotlib import pyplot
#plt.figure(1,figsize=(10,10))

sns.set_style("whitegrid", {'axes.grid' : False})

plt.figure(figsize=(10,10))

df = pd.read_csv("df_pymongo_merged_preds.csv")

#------------------------------------------------------------------------
# boxplot bassin_emploi et Salaires
a4_dims = (12, 12)
fig, ax = pyplot.subplots(figsize=a4_dims)
# graphes salaire par rapport aux villes
df_salaire_ville=df[['Salaires','Bassin_emploi']]
#df['Salaires'].boxplot(df['Bassin_emploi'],grid=False, rot=45, fontsize=15)
ax = sns.boxplot(x=df['Bassin_emploi'], y=df['Salaires'], data=df)
ax.axes.set_title("Salaire/Ville",fontsize=15)
ax.set_xlabel("Bassin_emploi",fontsize=15)
ax.set_ylabel("Salaires",fontsize=15)
ax.tick_params(labelsize=15)
#sns.plt.show()

plt.savefig("Salaire_Bassin_Emploi.png")
plt.close()
#---------------------------------------------------------------
# boxplot Niveau d'étude et Salaires
a4_dims = (12, 12)
fig, ax = pyplot.subplots(figsize=a4_dims)
ax = sns.boxplot(x=df["Niveau d'études"], y=df['Salaires'], data=df)
ax.axes.set_title("Salaire/Niveau d'étude",fontsize=15)
ax.set_xlabel("Niveau d'étude",fontsize=15)
ax.set_ylabel("Salaires",fontsize=15)
ax.tick_params(labelsize=15)

fig.savefig("Niveau_Etude_Salaire.pdf", format="pdf", bbox_inches="tight", transparent=True, pad_inches=0)
plt.close()

#--------------------------------------------------------------------------------
# Experience et Salaires
a4_dims = (12, 12)
fig, ax = pyplot.subplots(figsize=a4_dims)
df['Experience']=round(df['Experience'],2)
ax = sns.boxplot(x=df['Experience'], y=df['Salaires'], data=df)
ax.set_xticklabels(ax.get_xticklabels(),rotation=30)
ax.axes.set_title("Salaire/Experience",fontsize=15)
ax.set_xlabel("Experience",fontsize=15)
ax.set_ylabel("Salaires",fontsize=15)
ax.tick_params(labelsize=15)

fig.savefig("Salaire_Experience.pdf", format="pdf", bbox_inches="tight", transparent=True, pad_inches=0)
plt.close()
#--------------------------------------------------------------------------------
# correlation chiffre d'affaire et Salaire
import scipy.stats as stats
a4_dims = (12, 12)
fig, ax = pyplot.subplots(figsize=a4_dims)
#df["log Chiffre"] = np.log(df["Chiffre"])
j=sns.jointplot(data=df, x='Salaires', y="Chiffre", kind='reg', color='g', height=12,size=15)
#j.set_title("Scatterplot et Histogrammes des Salaires avec les Chiffres d'Affaires des Entreprises")
j.annotate(stats.pearsonr, fontsize=18)
#ax.axes.set_title("Salaire/Chiffre",fontsize=25)
#ax.set_xlabel("Chiffre",fontsize=20)
#ax.set_ylabel("Salaires",fontsize=20)
#ax.tick_params(labelsize=15)
#ax.xlabel('Salaires', fontsize=18)
#ax.ylabel("Chiffre d'Affaires", fontsize=18)
#ax.tick_params(axis="both", labelsize=18)
#plt.legend(fontsize=20)
#plt.show()

j.savefig("Salair_Chiffre.pdf", format="pdf", bbox_inches="tight", transparent=True, pad_inches=0)
#plt.close()
# --------------------------------------------------------------------------------
# degouper la colonne contrat
def ungroup_delim(col, delim=','):
    """Split elements délimités avec une virgule dans la colonne considérée, stacking columnwise"""
    return col.str.split(delim, expand=True).stack()
# Apply the ungrouping function, and forward fill elements that aren't grouped.
#ungrouped = annonces['Contrat'].apply(ungroup_delim).ffill()
ungrouped_contrat=ungroup_delim(df['Contrat'], delim=',')
# Drop la colonne des indexes.
Contrat_ungroup = ungrouped_contrat.reset_index(drop=True)

# remplcer certains elements

Contrat_ungroup = Contrat_ungroup.replace(to_replace =['full time','full-time','permanent',' cdi'], value = 'cdi', regex = True) 
Contrat_ungroup = Contrat_ungroup.replace(to_replace =['short term','short-term',' cdd'], value = 'cdd', regex = True) 
# replace the matching strings 
Contrat_ungroup = Contrat_ungroup.replace(to_replace =['internship',' stage'], value = 'stage', regex = True) 

Contrat_ungroup= Contrat_ungroup.replace(to_replace =['apprentissage','professionnalisation',' alternance'], value = 'alternance', regex = True) 

Contrat_ungroup = Contrat_ungroup.replace(to_replace =['freelance','independent','independant',' indépendant'], value = 'indépendant', regex = True) 
Contrat_ungroup = Contrat_ungroup.replace(to_replace =['part time',' part-time'], value = 'part-time', regex = True) 

Contrat_ungroup = Contrat_ungroup.replace(to_replace = ['contract', 'contracts',' contract', ' contracts','student',' student'], value = np.nan) 
#----------------------------------------------------------------------------------

# Contrat et Salaires
a4_dims = (12, 12)
fig, ax = pyplot.subplots(figsize=a4_dims)
ax = sns.boxplot(x=Contrat_ungroup, y=df['Salaires'], data=df)
ax.set_xticklabels(ax.get_xticklabels(),rotation=45)
ax.axes.set_title("Salaire/Contrat",fontsize=15)
ax.set_xlabel("Contrat",fontsize=15)
ax.set_ylabel("Salaires",fontsize=15)
ax.tick_params(labelsize=15)


fig.savefig("Contrat_Salaire.pdf", format="pdf", bbox_inches="tight", transparent=True, pad_inches=0)
plt.close()


#----------------------------------------------------------------------------------


ax= sns.lmplot(x="Experience", y="Salaires", hue="position",
               truncate=True, height=5, aspect=.8, data=df, size=30, legend=True, legend_out=True,scatter_kws={'s':200})

plt.title("Relation entre Salaire et Experience % Métier", size=50)
plt.savefig("Position_Salaire.pdf", format="pdf", bbox_inches="tight", transparent=True, pad_inches=0)
new_labels = ['Data Analyst', 'Developpeur','Data Scientist','Business Intelligence','IT Architect']
for t, l in zip(ax._legend.texts, new_labels): t.set_text(l)

ax.set_axis_labels("Experience","Salaires")
sns.set(font_scale = 5)

# afficher les paramètres stat

import statsmodels.formula.api as smf

mod=smf.ols(formula='Salaires ~ position * Experience', data=df)

res = mod.fit()
print(res.summary())