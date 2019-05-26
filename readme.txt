-----README.TXT-----

Team Élephant projet
--------------------

Le logiciel dans ce dépôt crée un rapport d'une douzaine de pages avec les données scrapées pendant les 28 derniers jours du site web Indeed.fr. Les emplois d'intérêt sont ceux du secteur Big Data, par exemple Data Scientist, Data Analyst, Développeur et Spécialiste Business Intelligence.

Les fichiers, dans l'ordre dans lequel ils sont effectués, sont les suivants:
- Scrapping.py (qui scrape Indeed.fr);
- scrapping_companies.py (qui scrape pour les données financielles de chaque entreprise);
- import_and_preprocessing.py* (pour mettre les données en forme convenable);
- additional_companies_preprocessing.py (pour mettre les données financielles des entreprises en forme convenable);
- Prediction.py (qui crée les prédictions des salaires en utilisant SVM et Random Forest);
- viz_guillaume.py,
- soukeye_graphs.py,
- hugh-graphs.py* (qui font les graphes pour le rapport en utilisant les données);
- rapport_automatise_envoye.py* (qui écrit le rapport en LaTeX, en prenant les graphes, le publie en format PDF, puis l'envoie à l'adresse decidé).

Les programmes sont activés avec l'aide des fichiers .bat. Ces fichiers .bat permettent que les executions automatisées s'effectuent aux horaires désirées. Pour les besoins de ce produit, un nouveau rapport doit être envoyé chaque lundi à 9h30.

* - Fichier pour lequel hpsteele a écrit du code.
