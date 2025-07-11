# Groupe1_mgt_opl_env_dev_Evaluation

Projet de Groupe : Créez une Application Web Interactive avec Git, Streamlit et DuckDB

## Membre du groupe

    .Eva Debora ASSY

    .Tonny MVOUMBI

    .Ange Muriel KAMGUEM

## Présentation du Projet

    La transition vers les véhicules électriques (VE) transforme profondément le secteur de la mobilité.Contrairement aux véhicules thermiques, les VE présentent des spécificités : autonomie limitée,
    dépendance aux infrastructures de recharge, usure des batteries,impact du climat et des trajets sur la performance.

    Ce projet data vise à exploiter ces particularités pour analyser et optimiser l’usage des VE à partir de données
    réelles. L’objectif est de développer des visualisations pour :
        .Mieux comprendre les comportements de recharge et de conduite,

        .Évaluer l’impact des trajets et conditions sur l’autonomie,

        .Optimiser l’implantation des bornes,

        .Anticiper la dégradation des batteries.


## Installation

### 1. Cloner le projet

````bash
git clone https://github.com/ton-utilisateur/streamlit-dashboard-csv.git
cd streamlit-dashboard-csv


### 2. Installation des dependances

la commande ci-dessous vous permettra installer les dependance de l'application

```bash
pip install -r requirements.txt


### 3. Executer L'application

```bash
streamlit run app.py

##  Description des fonctionnalites

Ce projet est une application web interactive développée avec Streamlit.
Elle permet de téléverser un fichier CSV, de le charger dans une base DuckDB, et de visualiser des KPI clés dans un tableau de bord.


- Import  de fichiers CSV
  Permet à l'utilisateur d'importer le jeux de données Data ce trouvant dans le repertoire de l'application via une interface simple, avec validation du format et chargement automatique.

- Stockage et interrogation SQL avec DuckDB
  Les données sont chargées dans une base DuckDB en mémoire.

- Visualisation de KPI et des Graphes
  Affichage de KPI et des graphes est dynamyque grace à la fonction de filtrage que nous avons integré à l'application afin de permettre à l'utilsateur de décider des données qu'ils souhaite analyser .

- Gestion d'erreurs robuste
  En cas d'absence de données ou d’erreur de requête, l’application affiche des messages explicites et guide l’utilisateur automatiquement vers l’accueil.



### 4 repartition des Taches

 | Membre de l'équipe     | Rôle / Contribution principale                                  |
| ------------------------| --------------------------------------------------------------- |
| **Eva ASSY**            |   creation des KPI Et Des Visualisation                         |
| **Tonny MVOUMBI**       |   Creation et gestion de la page Home                           |
| **Ange Muriel**         |   creation des KPI Et Des Visualisation                         |
````
