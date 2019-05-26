-----README.TXT-----

Team �lephant projet
--------------------

Le logiciel dans ce zip cr�e un rapport d'une douzaine de pages avec les donn�es scrap�es pendant les 28 derniers jours du site web Indeed.fr. Les emplois d'int�r�t sont ceux du secteur Big Data, par exemple Data Scientist, Data Analyst, D�veloppeur et Sp�cialiste Business Intelligence.

Les fichiers, dans l'ordre dans lequel ils sont effectu�s, sont les suivants:
- Scrapping.py (qui scrape Indeed.fr);
- scrapping_companies.py (qui scrape pour les donn�es financielles de chaque entreprise);
- import_and_preprocessing.py (pour mettre les donn�es en forme convenable);
- additional_companies_preprocessing.py (pour mettre les donn�es financielles des entreprises en forme convenable);
- Prediction.py (qui cr�e les pr�dictions des salaires en utilisant SVM et Random Forest);
- viz_guillaume.py,
- soukeye_graphs.py,
- hugh-graphs.py (qui font les graphes pour le rapport en utilisant les donn�es);
- rapport_automatise_envoye.py (qui �crit le rapport en LaTeX, en prenant les graphes, le publie en format PDF, puis l'envoie � l'adresse decid�).

Les programmes sont activ�s avec l'aide des fichiers .bat. Ces fichiers .bat permettent que les executions automatis�es s'effectuent aux horaires d�sir�es. Pour les besoins de ce produit, un nouveau rapport doit �tre envoy� chaque lundi � 9h30. 