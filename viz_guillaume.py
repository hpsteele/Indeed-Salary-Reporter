import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import datetime
from matplotlib import pyplot
#plt.figure(1,figsize=(10,10))

sns.set_style("whitegrid", {'axes.grid' : False})

annonces = pd.read_csv("df_pymongo_merged_preds.csv")


sns.set(style="darkgrid")
import seaborn as sns


cols = ["stage", "cdi", "cdd", "alternance", "freelance"]
results_set = [annonces["Details"].loc[annonces[col]==1].count() for col in cols]
df = pd.DataFrame({'results_set': results_set}, index=cols)
ax=df.plot.bar(rot=90,figsize = (15, 15))
ax.set_title('Nombre de contrat parmis les offres relevées')
fig = ax.get_figure()   
fig.savefig('contract_count.pdf',bbox_inches='tight', transparent=True, pad_inches=0)

#plot le nombre de compétences
cols = ['c+', 'cassandra', 'd3', 'dashboard', 'dataiku', 'deeplearning', 'excel', 'hadoop', 'java', 'javascript', 'keras', 'kpi', 'machinelearning', 'maths', 'matlab', 'ml', 'mysql', 'nlp', 'nosql', 'numpy', 'pandas', 'php', 'physics', 'physique', 'powerpoint', 'python', 'pytorch', 'qlikview', 'r', 'rstudio', 'ruby', 'sas', 'scala', 'sci-kit', 'scikit', 'shiny', 'spark', 'sql', 'statistics', 'statistique', 'tensorflow', 'vba']
results_set2 = [annonces["Details"].loc[annonces[col]==1].count() for col in cols]
df = pd.DataFrame({'results_set2': results_set2}, index=cols)
ax1 = df.plot.bar(rot=90,figsize = (15, 15))
ax1.set_title('Nombre de compétences relevées')
fig = ax1.get_figure()   
fig.savefig('skills_count.pdf',bbox_inches='tight', transparent=True, pad_inches=0)

#plot les salaires selon les compétences
cols = ['c+', 'cassandra', 'd3', 'dashboard', 'dataiku', 'deeplearning', 'excel', 'hadoop', 'java', 'javascript', 'keras', 'kpi', 'machinelearning', 'maths', 'matlab', 'ml', 'mysql', 'nlp', 'nosql', 'numpy', 'pandas', 'php', 'physics', 'physique', 'powerpoint', 'python', 'pytorch', 'qlikview', 'r', 'rstudio', 'ruby', 'sas', 'scala', 'sci-kit', 'scikit', 'shiny', 'spark', 'sql', 'statistics', 'statistique', 'tensorflow', 'vba']
results_set3 = [annonces["Salaires"].loc[annonces[col]==1].mean() for col in cols]
df = pd.DataFrame({'results_set2': results_set3}, index=cols)
ax2 = df.plot.bar(rot=90,figsize = (15, 15))
ax2.set_title('Salaires associés à chaque compétence (moyenne)')
fig = ax2.get_figure() 
fig.savefig('skills_salary.pdf',bbox_inches='tight', transparent=True, pad_inches=0)

#plot les salaires banlieu vs centre ville
annonces.groupby(['Inner_City',"Bassin_emploi"]).mean()['Salaires'].unstack().plot(kind="bar",title="les salaires selon la localité centre villes vs banlieu")
plt.rcParams['figure.figsize'] = (15,15)
plt.savefig('salaires_banlieu_villes.pdf')
#plot les salaires selon la ville et la seniorité
annonces.groupby(['Seniority_simplified',"Bassin_emploi"]).mean()['Salaires'].unstack().plot(kind="bar",title="les salaires selon la seniorité et la ville")
plt.rcParams['figure.figsize'] = (15,15)
plt.savefig('salaires_selon_villesetseniority.pdf',bbox_inches='tight', transparent=True, pad_inches=0)

#plot les salaires selon la ville et le rôle
annonces.groupby(['position',"Bassin_emploi"]).mean()['Salaires'].unstack().plot(kind="bar",title="les salaires selon la ville et le rôle")
plt.rcParams['figure.figsize'] = (15,15)
plt.savefig('salaires_selon_villesetrele.pdf',bbox_inches='tight', transparent=True, pad_inches=0)

#vertical
f, (ax3, ax4,ax6) = plt.subplots(3,figsize=(15,15))
sns.set(style="darkgrid")
ax3 =sns.countplot(ax=ax3,x="Bassin_emploi", hue="Niveau d'études", data=annonces)
ax3.set_title('niveau etude')
ax4 = sns.countplot(ax=ax4,x="position", data=annonces)
ax4.set_title('nombre de poste selon le rôle')
ax6 = sns.countplot(ax=ax6,x="Bassin_emploi", hue="position", data=annonces)
ax6.set_title('nombre de poste selon le rôle et la ville')#Paris has a lot more of analysts
f.savefig('vertical_subplots.pdf',bbox_inches='tight', transparent=True, pad_inches=0)

#Or horizontale
fig, axs = plt.subplots(ncols=3,figsize=(15,15))
sns.countplot(x='Bassin_emploi', hue="Niveau d'études", data=annonces, ax=axs[0])
sns.countplot(x='position', data=annonces, ax=axs[1])
sns.countplot(x='Bassin_emploi', hue='position', data=annonces, ax=axs[2])
plt.savefig('Bassin_emploi_etudes.pdf',bbox_inches='tight', transparent=True, pad_inches=0)

annonces.groupby(['true_date',"position"]).count()['Details'].unstack().plot(title="Number of offer per role")
plt.rcParams['figure.figsize'] = (15, 15)
plt.savefig('offer_position.pdf')
annonces.groupby(['true_date',"Bassin_emploi"]).count()['Details'].unstack().plot(title="Number of offer per city")
plt.rcParams['figure.figsize'] = (15,15)
plt.savefig('offer_city.pdf',bbox_inches='tight', transparent=True, pad_inches=0)