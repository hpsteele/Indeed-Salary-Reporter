# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 17:16:48 2019

@author: Hugh
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import datetime
import geopandas as gpd

# Le style de Seaborn est exploité
sns.set_style("whitegrid", {'axes.grid' : False})

# On utilise les données avec les prédictions
df = pd.read_csv("df_pymongo_merged_preds.csv")

#On enlève des lignes sans "timestamp", "Company", "Details", ou "Title"
df = df[df["timestamp"].notna()]
df = df[df["Company"].notna()]
df = df[df["Details"].notna()]
df = df[df["Title"].notna()]
df["timestamp"] = pd.to_datetime(df["timestamp"],infer_datetime_format=True)

"""
Fonction: vraie_date
Entrée: pd.DataFrame df
Sortie: pd.Series(datetime) des dates de publication de chaque ligne
"""
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

# On utilise vraie_date pour créer une colonne de dates correctes
df["vraie_date"] = vraie_date(df)

# Résultats des dernières semaines
past_28 = df.loc[(pd.datetime.today() - df["vraie_date"]).dt.days <= 28]
past_7 = df.loc[(pd.datetime.today() - df["vraie_date"]).dt.days <= 7]

# On trouve le nombre d'offres par date dans le mois
day_job_counts = past_28["vraie_date"].dt.date.value_counts().sort_index().reset_index()
day_job_counts.columns = ["Date", "Offres"]

# On donne les noms plus formels aux types de job
df["Position Type"] = df["position"].fillna("Miscellaneous")

df.loc[df["Position Type"] == "analyst", "Position Type"] = "Data Analyst"
df.loc[df["Position Type"] == "scientist", "Position Type"] = "Data Scientist"
df.loc[df["Position Type"] == "Business_Intelligence", "Position Type"] = "Business Intelligence"
df.loc[df["Position Type"] == "IT_architect", "Position Type"] = "IT Architect"

# Répétition pour assurer que les lignes soient correctes
past_28 = df.loc[(pd.datetime.today() - df["vraie_date"]).dt.days <= 28]
past_7 = df.loc[(pd.datetime.today() - df["vraie_date"]).dt.days <= 7]

dates_types = df[["vraie_date", "Position Type"]]
dates_types["Count"] = 1
dates_types["vraie_date"] = dates_types["vraie_date"].dt.date
#dates_types.groupby(by=dates_types.columns).sum()

jobby = dates_types.groupby(["vraie_date", "Position Type"]).count().reset_index()#.set_index(["vraie_date"])

# Une fonction pour réplique la fonction expand_grid en R
# Trouvé en ligne dans le site de Pandas (citation nécessaire - I'll find it!)
import itertools

vraie_date_col = pd.Series(pd.date_range(start=pd.datetime.today() - pd.Timedelta("28 days"), end=pd.datetime.today())).dt.date
pos_type_col = pd.Series(["Business Intelligence", "Data Analyst", "Data Scientist", "Developpeur", "IT Architect", "Miscellaneous"])

def expand_grid(dct):
    rows = itertools.product(*dct.values())
    return pd.DataFrame.from_records(rows, columns=dct.keys())

# On remplie les trous dans les dates du DataFrame
attempt = expand_grid({"date": vraie_date_col, "pos": pos_type_col})
attempt["Count2"] = 0
attempt2 = attempt.merge(jobby, how="left", left_on=["date", "pos"], right_on=["vraie_date", "Position Type"])
attempt3 = attempt2.drop(columns=["vraie_date", "Position Type"]).set_index(["date", "pos"])
date_pos_counts = attempt3.sum(axis=1)
date_pos_counts = date_pos_counts.reset_index()
date_pos_counts.columns = ["Date", "Position", "Number"]

# On crée des series pour chaque type de job
bi_counts = date_pos_counts.loc[date_pos_counts["Position"] == "Business Intelligence"]
da_counts = date_pos_counts.loc[date_pos_counts["Position"] == "Data Analyst"]
ds_counts = date_pos_counts.loc[date_pos_counts["Position"] == "Data Scientist"]
de_counts = date_pos_counts.loc[date_pos_counts["Position"] == "Developpeur"]
it_counts = date_pos_counts.loc[date_pos_counts["Position"] == "IT Architect"]
mi_counts = date_pos_counts.loc[date_pos_counts["Position"] == "Miscellaneous"]

bi_counts = bi_counts.drop(columns=["Position"]).set_index("Date")
da_counts = da_counts.drop(columns=["Position"]).set_index("Date")
ds_counts = ds_counts.drop(columns=["Position"]).set_index("Date")
de_counts = de_counts.drop(columns=["Position"]).set_index("Date")
it_counts = it_counts.drop(columns=["Position"]).set_index("Date")
mi_counts = mi_counts.drop(columns=["Position"]).set_index("Date")

# On les merge...
job_type_counts = pd.concat([de_counts, da_counts, ds_counts, bi_counts, it_counts, mi_counts], axis=1)
job_type_counts.columns = ["Developpeur", "Data Analyst", "Data Scientist", "Business Intelligence", "IT Architect", "Miscellaneous"]

# Stacked Area plot (Jobs vs. Time)
plot = job_type_counts.plot.area(figsize=(8, 6), title="Nombre d'emplois pendant les 28 derniers jours")
fig = plot.get_figure()
fig.savefig("job-numbers-stacked-date.pdf", format="pdf", bbox_inches="tight", transparent=True, pad_inches=0)

# On prend les nombres de chaque type d'emploi pendant le mois
job_time_sum = job_type_counts.iloc[:,:].sum().to_frame()
job_time_sum.columns = ["Breakdown"]

# Camembert (Percentage of each job type in the month)
plot = job_time_sum.plot.pie(y="Breakdown", figsize=(6,6), legend=False, title="Job Types of the past 28 days")
fig = plot.get_figure()
fig.savefig("job-numbers-type-pie.pdf", format="pdf", bbox_inches="tight", transparent=True, pad_inches=0)

# Extraire les numéros de départmente de "Location"
df["Department"] = df["Location"].str.extract(r'(\d\d)', expand=False)
past_28["Department"] = past_28["Location"].str.extract(r'(\d\d)', expand=False)

# Dictionnaire Region -> Department
dept_to_region = {"Hauts-de-France": ['02', "60", "80", "62", "59"], "Normandie": ["50", "14", "61", "27", "76"],
                  "Bretagne": ["29", "22", "35", "56"], "Grand Est": ["08", "51", "10", "52", "55", "54", "57", "88", "67", "68"],
                  "Pays de la Loire": ["53", "44", "72", "49", "85"], "Paris": ["75"],
                  "Banlieues": ["78", "95", "77", "91", "92", "93", "94"], "Centre Val de Loire": ["28", "18", "36", "37", "41", "45"],
                   "Bourgogne-Franche-Comté": ["89", "58", "21", "71", "70", "90", "25", "39"], 
                   "Auvergne-Rhone-Alpes": ["03", "63", "15", "43", "42", "07", "69", "26", "38", "01", "74", "73"], 
                  "Nouvelle Aquitaine": ["79", "86", "16", "17", "23", "87", "19", "24", "33", "47", "40", "64"],
                   "Occitanie": ["46", "12", "82", "81", "31", "32", "09", "65", "48", "30", "34", "11", "66"], 
                   "PACA": ["05", "06", "04", "83", "84", "13"]}

# Deux fonctions pour donner les régions pour chaque département
# Avec Paris et Banlieues séparés...
def to_region(x):
    for region in dept_to_region.keys():
        if x in dept_to_region[region]:
            return region
    return np.nan

# ...et Ensemble
def to_true_region(x):
    if to_region(x) in ["Paris", "Banlieues"]:
        return "Ile-de-France"
    return to_region(x)

# Et on crée sa colonne
past_28["Region"] = past_28["Department"].apply(to_true_region)

#past_month = df.loc[(pd.datetime.today() - df["vraie_date"]).dt.days <= 28]

# Nombre d'emplois par Région
job_place_sum = past_28.set_index("vraie_date")["Region"].value_counts().reset_index()
job_place_sum.columns = ["Region", "Offres"]

# Une carte pour la France
france_map = gpd.read_file("regions_2015_metropole_region.shp")

regions = list(dept_to_region.keys()) + ["Ile-de-France", "Corse"]
ordering = [3, 10, 9, 1, 8, 2, 7, 14, 13, 11, 0, 4, 12]
regions = [regions[i] for i in ordering]

france_map["Region"] = regions
france_map = france_map.set_index(["Region"])

# log_Offres est pour le heatmap
france_map["Offres"] = past_28["Region"].value_counts()
france_map["log_Offres"] = france_map["Offres"]**0.5 #np.log(france_map["Offres"] + 1)
france_map = france_map.fillna(0)

# Coordinées pour le numéro pour chaque région
france_map['coords'] = france_map['geometry'].apply(lambda x: x.representative_point().coords[:])
france_map['coords'] = [coords[0] for coords in france_map['coords']]

# Heatmap Cartographique
fig1, ax1 = plt.subplots(figsize=(6,6))
france_map.plot(column="log_Offres", cmap="Greys", linewidth=0.8, edgecolor="0.8", ax=ax1)#, legend=True)
# Si la région est trop foncée son numéro devient blanc
for idx, row in france_map.iterrows():
    if row["log_Offres"] > france_map["log_Offres"].max()/2:
        color = "white"
    else:
        color = "black"
    ax1.annotate(s=int(row['Offres']), xy=row['coords'],
                 horizontalalignment='center', color=color, fontsize=12)

ax1.set_yticks([])
ax1.set_xticks([])
ax1.set_title("Nombre d'Offres dans chaque Région")

fig1.savefig("france-job-numbers-map.pdf", format="pdf", bbox_inches="tight", transparent=True, pad_inches=0)

# Même chose, mais avec Ile-de-France
idf_depts = dept_to_region["Paris"] + dept_to_region["Banlieues"]
idf_depts
dept_job_counts = past_28["Department"].value_counts()[idf_depts].to_frame()
dept_job_counts.columns = ["Offres"]

idf_map = gpd.read_file("geoflar-departements.shp")

idf_map = idf_map.set_index("code_dept")

idf_map['coords'] = idf_map['geometry'].apply(lambda x: x.representative_point().coords[:])
idf_map['coords'] = [coords[0] for coords in idf_map['coords']]

idf_map["Offres"] = dept_job_counts
idf_map["log_Offres"] = idf_map["Offres"]**0.5 #np.log(dept_job_counts)

fig2, ax2 = plt.subplots(figsize=(12,12))
idf_map.plot(column="log_Offres", cmap="Greys", linewidth=0.8, edgecolor="0.8", ax=ax2)#, legend=True)
for idx, row in idf_map.iterrows():
    if row["log_Offres"] > idf_map["log_Offres"].max()/2:
        color = "white"
    else:
        color = "black"
    ax2.annotate(s=int(row['Offres']), xy=row['coords'],
                 horizontalalignment='center', color=color, fontsize=12)

ax2.set_yticks([])
ax2.set_xticks([])
ax2.set_title("Nombre d'Offres dans chaque Département")

fig2.savefig("jobs-idf-map.pdf", format="pdf", bbox_inches="tight", transparent=True, pad_inches=0)

# Même chose beaucoup de fois mais avec beaucoup de types d'emplo
for job in ["Developpeur", "Data Analyst", "Data Scientist", "Business Intelligence", "IT Architect"]:
    france_map["Offres " + job] = past_28.loc[past_28["Position Type"] == job, "Region"].value_counts()
    idf_map["Offres " + job] = past_28.loc[past_28["Position Type"] == job, "Department"].value_counts()
    france_map["log_Offres " + job] = france_map["Offres " + job]**0.5 #np.log(france_map["Offres " + job])
    idf_map["log_Offres " + job] = idf_map["Offres " + job]**0.5 #np.log(idf_map["Offres " + job])

france_map = france_map.fillna(0)
idf_map = idf_map.fillna(0)

france_map['coords'] = france_map['geometry'].apply(lambda x: x.representative_point().coords[:])
france_map['coords'] = [coords[0] for coords in france_map['coords']]

graphs = ["Developpeur", "Data Analyst", "Data Scientist", "Business Intelligence"]#, "IT Architect"] #["", 
graph_colors = ["Blues", "Oranges", "Greens", "BuPu", "Reds"]
fig_off, ax_off = plt.subplots(len(graphs),2,figsize=(12,20))
fig_off.subplots_adjust(wspace=0.02, hspace=0.02)

for i in range(len(graphs)):
    france_map.plot(column="log_Offres " + graphs[i], cmap=graph_colors[i], linewidth=0.8, edgecolor="0.8", ax=ax_off[i,0])#, legend=True)
    for idx, row in france_map.iterrows():
        if row["log_Offres " + graphs[i]] > france_map["log_Offres " + graphs[i]].max()/2:
            color = "white"
        else:
            color = "black"
        ax_off[i,0].annotate(s=int(row['Offres ' + graphs[i]]), xy=row['coords'], 
                        horizontalalignment='center', color=color, fontsize=12)

    idf_map.plot(column="log_Offres " + graphs[i], cmap=graph_colors[i], linewidth=0.8, edgecolor="0.8", ax=ax_off[i,1])#, legend=True)
    for idx, row in idf_map.iterrows():
        if row["log_Offres " + graphs[i]] > idf_map["log_Offres " + graphs[i]].max()/2:
            color = "white"
        else:
            color = "black"
        ax_off[i,1].annotate(s=int(row['Offres ' + graphs[i]]), xy=row['coords'],
                 horizontalalignment='center', color=color, fontsize=12)
        
    ax_off[i,0].set_yticks([])
    ax_off[i,0].set_xticks([])
    ax_off[i,1].set_yticks([])
    ax_off[i,1].set_xticks([])
    ax_off[i,0].set_ylabel(graphs[i])

fig_off.suptitle("Nombre d'Offres d'Emplois Big Data (28 derniers jours)", y=0.9)
fig_off.savefig("job-numbers-many-maps.pdf", format="pdf", bbox_inches="tight", transparent=True, pad_inches=0)

# Tous les emplois ensemble encore, mais ensemble dans une figure 1x2
figgg, (axx1, axx2) = plt.subplots(1,2,figsize=(11, 7))
france_map.plot(column="log_Offres", cmap="Greys", linewidth=0.8, edgecolor="0.8", ax=axx1)#, legend=True)

axx1.set_yticks([])
axx1.set_xticks([])
axx2.set_yticks([])
axx2.set_xticks([])

for idx, row in france_map.iterrows():
    if row["log_Offres"] > france_map["log_Offres"].max()/2:
        color = "white"
    else:
        color = "black"
    axx1.annotate(s=int(row['Offres']), xy=row['coords'],
                 horizontalalignment='center', color=color, fontsize=12)
    
idf_map.plot(column="log_Offres", cmap="Greys", linewidth=0.8, edgecolor="0.8", ax=axx2)#, legend=True)
for idx, row in idf_map.iterrows():
    if row["log_Offres"] > idf_map["log_Offres"].max()/2:
        color = "white"
    else:
        color = "black"
    axx2.annotate(s=int(row['Offres']), xy=row['coords'],
                 horizontalalignment='center', color=color, fontsize=12)

figgg.suptitle("Nombre d'Offres d'Emplois Big Data (28 derniers jours)", y=0.8)
figgg.savefig("big-maps.pdf", format="pdf", bbox_inches="tight", transparent=True, pad_inches=0)