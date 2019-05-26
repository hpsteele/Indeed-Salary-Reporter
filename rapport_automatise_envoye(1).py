# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 15:41:07 2019
Updated on Tue Mar 12 12:15:00 2019
Updated on Wed Apr  3 15:30:00 2019

@author: Hugh - Team Elephant

Un programme pour écrire et produire les rapports automatisés vers les fichiers HTML
et PDF, puis les envoyer vers le recipient désiré.
Fonctions:  phrase_num_jobs(_fr), phrase_avg_sal(_fr), ecrit_pdf, send_email.
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import yagmail #gmail
import keyring #mdp
import os #latex compile
import datetime

# On utilise le dataframe avec les prédictions pour le texte automatisé
df = pd.read_csv("df_pymongo_merged_preds.csv")

# true_date devient une vraie date
df["true_date"] = pd.to_datetime(df["true_date"])

# Une colonne pour les postes qui a l'air un peu mieux est créée
df["Position Type"] = df["position"].copy()
df.loc[df["Position Type"] == "analyst", "Position Type"] = "Data Analyst"
df.loc[df["Position Type"] == "scientist", "Position Type"] = "Data Scientist"
df.loc[df["Position Type"] == "Business_Intelligence", "Position Type"] = "Business Intelligence"
df.loc[df["Position Type"] == "IT_architect", "Position Type"] = "IT Architect"
df["Position Type"] = df["Position Type"].fillna("Miscellaneous")

# Des dataframes pour les derniers jours
fortnight = (pd.datetime.today() - df["true_date"]).dt.days <= 14
week = (pd.datetime.today() - df["true_date"]).dt.days <= 7

past_week = df.loc[week]
week_before = df.loc[fortnight & ~week]

"""
Fonction: phrase_num_jobs (Job Numbers)
Entrées: pd.DataFrame past_week, pd.DataFrame week_before
Sortie: String phrase primaire, List(String) des sous phrases (bullet points)
"""
def phrase_num_jobs(past_week, week_before):
    if week_before.shape[0] == 0:
        if past_week.shape[0] == 0:
            return "There were no job openings found in the past two weeks. Sorry about that!", []
        phrase = "From zero, the number of job openings in critical areas has increased to " + str(past_week.shape[0] - week_before.shape[0]) + ". The breakdown into different job types is as follows: "
        job_week = past_week["Position Type"].value_counts()
        job_week = (100 * job_week / job_week.sum()).sort_values().to_frame()
        job_week.columns = ["Percentages"]
        
        job_week["Phrases"] = job_week.apply(lambda x: str(x.index) + " - " + str(x["Percentages"]))
        phrase_list = job_week["Phrases"].tolist()
        return phrase, phrase_list

    phrase = "The number of job openings in critical areas has "
    change = 100*(past_week.shape[0] - week_before.shape[0]) / week_before.shape[0]
    if change == 0:
        phrase += ", surprisingly, remained exactly the same. The breakdown into different job types is as follows: "
        job_week = past_week["Position Type"].value_counts().to_frame()
        job_week.columns = ["Totals"]
        job_week["Percentages"] = job_week["Totals"] / job_week.shape[0]
        job_week["Phrases"] = job_week.apply(lambda x: str(x.index) + " - " + str(x["Totals"]) + " (" + x["Percentages"] + ")")
        return phrase, phrase_list
        
    if change > 0:
        phrase += "increased by " 
    else:
        phrase += "decreased by "
    phrase += str(np.around(abs(change),1)) + "\%:"
    
    changes = past_week["Position Type"].value_counts() - week_before["Position Type"].value_counts()    
    changes /= week_before["Position Type"].value_counts()
    changes *= 100
    changes = np.around(changes, 1)
    
    data = pd.concat([changes, past_week["Position Type"].value_counts()], axis=1).reset_index()
    data.columns = ["Position", "Change", "Total"]
    
    def up_or_down(x):
        if x == 0:
            return "remain stable at "
        if x > 0:
            return "are up " + str(abs(x)) + "\% to "
        return "are down " + str(abs(x)) + "\% to "
    
    data["Phrase_Change"] = data["Change"].apply(up_or_down)
    data["Sentences"] = data["Position"] + " - Numbers " + data["Phrase_Change"] + data["Total"].astype(str)
    
    
    return phrase, data["Sentences"].tolist()

"""
Fonction phrase_avg_sal (Average Salary)
Entrées: pd.DataFrame past_week, pd.DataFrame week_before
Sorties: String phrase primaire, List(String) sous phrases (bullet points)
"""
def phrase_avg_sal(past_week, week_before):
    if week_before.shape[0] == 0:
        if past_week.shape[0] == 0:
            return "", []
        phrase = "The median salaries in those areas as follows: "
        job_week = past_week[["Position Type", "salaire_forest"]].groupby(by=["Position Type"]).median()
        
        job_week["Phrases"] = job_week.apply(lambda x: str(x.index) + " - " + str(np.around(x["salaire_forest"])))
        phrase_list = job_week["Phrases"].tolist()
        return phrase, phrase_list

    phrase = "The median salary in critical areas has "
    change = 100*(past_week.shape[0] - week_before.shape[0]) / week_before.shape[0]
    if change == 0:
        phrase += ", surprisingly, remained stable since last week."
    elif change > 0:
        phrase += "increased since last week."
    else:
        phrase += "decreased since last week."
    phrase += " The breakdown into different job types is as follows:"   
         
    job_week = past_week[["Position Type", "salaire_forest"]].groupby(by=["Position Type"]).median().reset_index()
    data = job_week["Position Type"] + " - " + np.around(job_week["salaire_forest"],-2).astype(int).astype(str) + " Euro per annum"
    
    return phrase, data.tolist()

"""
Fonction: phrase_num_jobs_fr (version francaise de phrase_num_jobs)
"""
def phrase_num_jobs_fr(past_week, week_before):
    if week_before.shape[0] == 0:
        if past_week.shape[0] == 0:
            return "Il n'y a pas de nouvelles annonces depuis 2 semaines.  D\\'esol\\'e !", []
        phrase = "De 0, le nombre d'annonces a augment\\'e jusqu'\`a " + str(past_week.shape[0] - week_before.shape[0]) + ". La r\\'epartition par cat\\'egorie de poste est la suivante :"
        job_week = past_week["Position Type"].value_counts()
        job_week = (100 * job_week / job_week.sum()).sort_values().to_frame()
        job_week.columns = ["Percentages"]
        
        job_week["Phrases"] = job_week.apply(lambda x: str(x.index) + " - " + str(x["Percentages"]))
        phrase_list = job_week["Phrases"].tolist()
        return phrase, phrase_list

    phrase = "Le nombre d'offres d'emplois dans cette zone est "
    change = 100*(past_week.shape[0] - week_before.shape[0]) / week_before.shape[0]
    if change == 0:
        phrase += ", \\'etonnamment, rest\\'e exactement le m\\^eme. La r\\'epartition par diff\\'erents types de postes est la suivante : "
        job_week = past_week["Position Type"].value_counts().to_frame()
        job_week.columns = ["Totals"]
        job_week["Percentages"] = job_week["Totals"] / job_week.shape[0]
        job_week["Phrases"] = job_week.apply(lambda x: str(x.index) + " - " + str(x["Totals"]) + " (" + x["Percentages"] + ")")
        return phrase, phrase_list
        
    if change > 0:
        phrase += "augment\\'e \\`a " 
    else:
        phrase += "diminu\\'e \\`a "
    phrase += str(np.around(abs(change),1)) + "\%:"
    
    changes = past_week["Position Type"].value_counts() - week_before["Position Type"].value_counts()    
    changes /= week_before["Position Type"].value_counts()
    changes *= 100
    changes = np.around(changes, 1)
    
    data = pd.concat([changes, past_week["Position Type"].value_counts()], axis=1).reset_index()
    data.columns = ["Position", "Change", "Total"]
    
    def up_or_down(x):
        if x == 0:
            return "reste stable \`a "
        if x > 0:
            return "s'augmente " + str(abs(x)) + "\% \`a "
        return "se diminue " + str(abs(x)) + "\% \`a "
    
    data["Phrase_Change"] = data["Change"].apply(up_or_down)
    data["Sentences"] = data["Position"] + " - Le nombre " + data["Phrase_Change"] + data["Total"].astype(str)
    
    
    return phrase, data["Sentences"].tolist()

"""
Fonction: phrase_avg_sal_fr (version francaise de phrase_avg_sal)
"""
def phrase_avg_sal_fr(past_week, week_before):
    if week_before.shape[0] == 0:
        if past_week.shape[0] == 0:
            return "", []
        phrase = "Le salaire m\\'edian dans ces zones est le suivant: "
        job_week = past_week[["Position Type", "salaire_forest"]].groupby(by=["Position Type"]).median()
        
        job_week["Phrases"] = job_week.apply(lambda x: str(x.index) + " - " + str(np.around(x["salaire_forest"])))
        phrase_list = job_week["Phrases"].tolist()
        return phrase, phrase_list

    phrase = "Le salaire m\\'edian dans ces zones est "
    change = 100*(past_week.shape[0] - week_before.shape[0]) / week_before.shape[0]
    if change == 0:
        phrase += ", \\'etonnament, rest\\'e stable depuis la semaine derni\\`ere."
    elif change > 0:
        phrase += "augment\\'e depuis la semaine derni\\`ere."
    else:
        phrase += "diminu\\'e depuis la semaine derni\`ere."
    phrase += " La r\\'epartition en diff\\'erentes cat\\'egories de postes est la suivante :"   
         
    job_week = past_week[["Position Type", "salaire_forest"]].groupby(by=["Position Type"]).median().reset_index()
    data = job_week["Position Type"] + " - " + np.around(job_week["salaire_forest"],-2).astype(int).astype(str) + " Euro par ann\\'ee"
    
    return phrase, data.tolist()

stats_en = {phrase_num_jobs(past_week, week_before)[0]: phrase_num_jobs(past_week, week_before)[1]}
stats_en[phrase_avg_sal(past_week, week_before)[0]] = phrase_avg_sal(past_week, week_before)[1]
stats_fr = {phrase_num_jobs_fr(past_week, week_before)[0]: phrase_num_jobs_fr(past_week, week_before)[1]}
stats_fr[phrase_avg_sal_fr(past_week, week_before)[0]] = phrase_avg_sal_fr(past_week, week_before)[1]

# Fonction: ecrit_pdf
# Entrées:  String suffix (fin des noms de fichier pour les graphes).
# Actions:  Crée un fichier "Job_Market_Analysis_[suffix].pdf" pour le
#           rapport avec les graphes désirés.
# Sortie:   Nom de fichier du rapport PDF.
def ecrit_pdf(suffix):

    title_page = """
    \\documentclass[12pt]{report}
    \\usepackage[english]{babel}
    \\usepackage{url}
    \\usepackage[utf8x]{inputenc}
    \\usepackage{amsmath}
    \\usepackage{graphicx}
    \\graphicspath{{images/}}
    \\usepackage{parskip}
    \\usepackage{fancyhdr}
    \\usepackage{vmargin}
    \\setmarginsrb{3 cm}{2.5 cm}{3 cm}{2.5 cm}{1 cm}{1.5 cm}{1 cm}{1.5 cm}
    \\usepackage[ddmmyyyy]{datetime}
    \\renewcommand{\dateseparator}{/}
    \\usepackage{rotating}
    
    \\title{Rapport Hebdomadaire}								
    \\author{Team Elephant}						
    \\date{\today}

    \\makeatletter
    \\let\\thetitle\@title
    \\let\\theauthor\@author
    \\let\\thedate\@date
    \\makeatother

    \\pagestyle{fancy}
    \\fancyhf{}
    \\rhead{\\theauthor}
    \\lhead{\\thetitle}
    \\cfoot{\\thepage}
    
    \\begin{document}

    \\begin{titlepage}
    	\\centering
        \\vspace*{0.5 cm}
        % \\includegraphics[scale = 0.075]{bsulogo.png}\\\\[1.0 cm]
        \\begin{center}    \\textsc{\Large   Team Elephant}\\\\[2.0 cm]	\\end{center}
        {\Large \\today }\\\\[0.5 cm] % xtsc at beginning
        \\rule{\linewidth}{0.2 mm}\\\\[0.4 cm]
	    { \\huge \\bfseries \\thetitle}\\\\
	    \\rule{\linewidth}{0.2 mm}\\\\[1.5 cm]
	
  	    \\begin{minipage}{0.4\\textwidth}
  		    \\begin{flushleft} \\large
             % h{Submitted To:}\\\\
		    
	        \\end{flushleft}
	    \\end{minipage}~
	    \\begin{minipage}{0.4\\textwidth}
            
		    \\begin{flushright} \\large
		    \\emph{Auteurs :} \\\\
		     Soukeye CISSE \\\\
		     Celia CLEMENTS \\\\
		     Guillaume LABAS \\\\
		     Philippe PASCUAL \\\\
		     Hugh STEELE
	        \\end{flushright}
           
	    \\end{minipage}\\\\[2 cm]
	
        \\includegraphics[scale = 0.2]{ElephantPic.png}
    
    \\end{titlepage}
    
    """
    
    overview_page = """
    \\section{Overview}
 
    The following document contains graphical data pertaining to the job market across regions of France, particularly the major metropolitan areas such as Paris, Toulouse, Lyon, Nantes and Bordeaux. The job types that have been accounted for are those in the data sector, namely those of data science, data analysis, business intelligence, program development and IT architecture.
    
    Most of our graphical data concerns the past 4 weeks, thus showing the market in a comparatively recent state. However, we provide a text overview of the past 7 days as well, giving a truly up-to-date picture.

    \\begin{itemize}\n"""
    
    for stat in stats_en.keys():
        overview_page += "\\item " + stat + " \n"
        if len(stats_en[stat]) != 0:
            overview_page += "\\begin{itemize} \n"
            for substat in stats_en[stat]:
                overview_page += "\\item " + substat + " \n"
            overview_page += "\\end{itemize} \n"
        
    overview_page += """

    \\end{itemize}

    \\newpage
    
    \\section{Sommaire}
 
    Ce document contient des donn\\'ees graphiques qui concernent le march\\'e de l'emploi dans toute la France, en particulier dans les zones m\\'etropolitaines comme Paris, Toulouse, Lyon, Nantes et Bordeaux. Les types d'emplois que nous avons pris en compte sont li\\'es au secteur du Big Data, \\`a savoir Data Science, Data Analysis, Business Intelligence, ainsi que le d\'eveloppement de logiciels et l'architecture informatique. La plupart de nos graphiques utilisent les donn\\'ees des 4 derni\\`eres semaines, et montrent donc le march\'e dans son \\'etat assez r\\'ecent. Cependant, nous fournissons un r\\'esum\\'e en texte des 7 derniers jours aussi pour offrir une vision aussi actualis\\'ee que possible.

    \\begin{itemize}\n"""

    for stat in stats_fr.keys():
        overview_page += "\\item " + stat + " \n"
        if len(stats_fr[stat]) != 0:
            overview_page += "\\begin{itemize} \n"
            for substat in stats_fr[stat]:
                overview_page += "\\item " + substat + " \n"
            overview_page += "\\end{itemize} \n"
        
    overview_page += """ 

    \\end{itemize}
    
    \\newpage

    \\section{Nombre d'Offres}

    \\noindent\makebox[\\textwidth]{\includegraphics[width=0.4\paperheight]{job-numbers-stacked-date.pdf}}
    
    \\noindent\makebox[\\textwidth]{\includegraphics[width=0.3\paperheight]{job-numbers-type-pie.pdf}}
 
    \\begin{sidewaysfigure}
    \\noindent\makebox[\\textwidth]{\includegraphics[width=0.7\paperheight]{big-maps.pdf}}
    \\end{sidewaysfigure}
    
    \\noindent\makebox[\\textwidth]{\includegraphics[height=0.7\paperheight]{job-numbers-many-maps.pdf}}
    
    \\newpage

    \\section{Estimates of Salaries}
    
    \\vspace{2cm}
    
    \\noindent\makebox[\\textwidth]{\includegraphics[width=0.8\paperwidth]{salaires_selon_villesetrele.pdf}}
    
    \\newpage
    
    \\vspace*{2.5cm}
    
    \\noindent\makebox[\\textwidth]{\includegraphics[width=0.8\paperwidth]{salaires_selon_villesetseniority.pdf}}

    \\newpage
    
    \\vspace*{2.5cm}
    
    \\noindent\makebox[\\textwidth]{\includegraphics[width=0.8\paperwidth]{Contrat_Salaire.pdf}}
    
    \\newpage
    
    \\vspace*{2.5cm}
    
    \\noindent\makebox[\\textwidth]{\includegraphics[width=0.8\paperwidth]{Niveau_Etude_Salaire.pdf}}
    
    \\newpage
    
    \\vspace*{2.5cm}
    
    \\noindent\makebox[\\textwidth]{\includegraphics[width=0.8\paperwidth]{Salair_Chiffre.pdf}}
    
    \\newpage
    
    \\vspace*{2.5cm}
    
    \\noindent\makebox[\\textwidth]{\includegraphics[width=0.8\paperwidth]{Position_Salaire.pdf}}

    \\section{Skill Sets}
 
    \\vspace{2cm}
    
    \\noindent\makebox[\\textwidth]{\includegraphics[width=0.8\paperwidth]{skills_salary.pdf}}
    
    \\newpage
    
    \\vspace*{2.5cm}
    
    \\noindent\makebox[\\textwidth]{\includegraphics[width=0.8\paperwidth]{skills_count.pdf}}
    
    \\newpage
    

    \\end{document}

"""

    # Nom du fichier = "Job_Market_Analysis_[date].tex"
    g = open("Job_Market_Analysis_{}.tex".format(suffix),"w")
    g.write(title_page + overview_page)
    g.close()

    # Crée "Job_Market_Analysis_[date].pdf"
    os.system("pdflatex Job_Market_Analysis_{}.tex".format(suffix))
    
    return "Job_Market_Analysis_{}.pdf".format(suffix)

# Fonction: send_email
# Entrées:  String send_address, String recipient, String rec_address
#           String attached pdf
# Actions:  Envoie de l'adresse "send_address" de Team Elephant à l'adresse
#           gmail "rec_address" de "recipient" (le nom auquel le mail est 
#           adressé), avec les pièces jointes (facultatives).
# Sortie:   Rien
def send_email(send_address, recipient, rec_address, pdf):
    today= datetime.datetime.today().strftime("%d/%m/%Y")
    
    body = """
    {},
    
    Veuillez trouver ci-joint votre dernier rapport concernant les offres d'emploi qui vous intéressent.
    
    Bien cordialement,
    
    Team Elephant
    """.format(recipient) # Texte du mail
    
    subject = "Dev & Data Job Market Analysis - " + today
    
    attachments = [pdf]
    
    # Keyring doit contenir le mot de passe
    yag = yagmail.SMTP(send_address,
                       keyring.get_password("yagmail", send_address))
    
    yag.send(to=rec_address,
             subject=subject,
             contents=body,
             attachments=attachments)
    return

# Toutes les fonctions ensemble
# Fonction: everything
# Entrées:  pd.DataFrame df, String send_address, String recipient,
#           String rec_address, String suffix
# Action:   Prend le dataframe df des données, crée les graphes pertinents,
#           crée le rapport avec les graphes en format PDF, et
#           envoie les résultats (tous avec la même suffixe) à rec_address
#           (l'adresse de recipient).
# Sortie:   Rien
# Défauts donnés avant...
send_address = "team.elephant.in.the.room@gmail.com"
rec_address = "team.elephant.in.the.room@gmail.com"
recipient = "Monsieur Fievet"
suffix = datetime.datetime.today().strftime("%d-%m-%Y")
def everything(df=df, send_address=send_address, recipient=recipient,
               rec_address=rec_address, suffix=suffix):
    
    send_email(send_address, recipient, rec_address, ecrit_pdf(suffix))
    
    return

everything()