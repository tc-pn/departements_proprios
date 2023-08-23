# -*- coding: utf-8 -*-
"""
Created on Wed Jul 5 15:12:52 2023

@author: Thomas Czuba

Dans ce petit projet je m'intéresse à la répartition des propriétaires 
en fonction du département, avant de faire une moyenne nationale par âge
Le fichier est fourni par l'INSEE, dont voici la référence :
Insee, Recensements de la population 2018 et 2019 et recensements généraux des COM, BPE 2020, Insee-DGFiP-Cnaf-Cnav-Ccmsa, Fichier localisé social et fiscal (Filosofi) 2019

"""
import pandas as pd 

# charger les infos du recensement de chaque circonsciption française aux législatives 2019
# en filtrant les infos des outre-mer, qui sont un cas particulier
df = pd.read_excel("indic-stat-circonscriptions-legislatives-2022.xlsx", skiprows = 7, skipfooter = 27)

# créer un dictionnaire des colonnes, à réutiliser avec le la feuille 2 du fichier excel
cols = df.columns

# détecter les circonscriptions restantes avec des valeurs manquantes, ici à part les outre mer
df_missing_values = df[df.isna().any(axis = 1)]
# résultat c'est Paris et l'Essonne
print(df_missing_values)

# quelles sont les informations manquantes justement ?
df_missing_info = df_missing_values.loc[:, df_missing_values.isna().any(axis = 0)]
list_missing_info = df_missing_info.columns 

# dans l'idéal, utiliser la seconde feuille excel pour avoir le nom précis de ces informations
print(list_missing_info)
# en attendant ça donne ça : 
# act_agr : Part de la population active agriculteur exploitant (en %)
# iranr_dep : Part des personnes résidant dans une autre commune du département un an auparavant (en %)
# ilt_dep : Part des actifs en emploi travaillant dans une autre commune du département  (en %)

# je ne m'explique pas le problème pour la 10eme circo de l'Essonne (c'est celle de Grigny),
# 21% de la surface étant classée comme rurale 
# peut-être qu'il n'y a pas d'exploitants ? Mais dans ce cas 0% fonctionnerait...

# Le 75 est un département dont les limites les mêmes que celles de Paris,
# iranr_dep et ilt_dep ne sont pas définis

# On a donc un choix entre i) changer la valeur à 0 ou bien ii) supprimer ces lignes
# Je préfère les mettre à 0 pour Paris et 
# supprimer la 10ème circo de l'Essonne puisque je ne la comprends pas

df.drop(df_missing_values.index[-1], inplace = True)
df.fillna(0, inplace = True)

# La Corse est non seulement un haut lieu touristique mais en plus pose problème pour la numérotation 
# de ses départements qui n'est pas juste numérique, je vais remplacer ces numéros de par de nouveaux,
# plus facilement exploitables

# on renumérote la Corse à 20 avant sa séparation entre Haute (2A) et Basse Corse (2B) en 1976
circo_corse = ['2A001','2A002','2B001','2B002']
nouveaux_id_corse = ['20001','20002','20003','20004']

df.replace(circo_corse, nouveaux_id_corse, inplace = True)

# Les données ont été cleanées, il reste maintenant à regarder les informations recherchées

colonnes = ['circo', 'Nom de la circonscription', 'proprio']

# je veux calculer le taux moyen de propriétaire par département, avec la déviation standard
# pour ça il suffit de rassembler les taux par département dans un nouveau dataframe

# ici seuls 
df["circo"] = pd.to_numeric(df["circo"]) / 1000.
df["circo"] = df["circo"].astype(int)

dic = {}
df_new = df.loc[1:,colonnes]

list_departements = []
for i in range(1,df_new["circo"].max()+1):
    foo = df[df["circo"].isin([i])]
    list_departements.append(foo.loc[foo.index[0],"Nom de la circonscription"].split(' - ')[0])
    dic[i] = [foo["proprio"].mean(),foo["proprio"].std()]
    
df_final = pd.DataFrame(dic, index = ["mean", "std"])
df_final.columns = list_departements

# on affiche enfin la moyenne des criconscriptions du taux de propriétaires par département
# ainsi que la déviation standard qui s'interprète comme la variabilité du taux de propriétaires dans
# les départements

print(df_final)
# Remarquons le taux très bas du Val-de-Marne mais avec une forte variabilité entre les circonscriptions
df_final = df_final.transpose()

print(df_final[df_final["mean"] == df_final["mean"].min()])
print(df_final[df_final["mean"] == df_final["mean"].max()])
# Paris est sans surprises le département avec le moins de proprios, avec 33%
# La Creuse est au sommet avec 72.5%, mais une déviation standard non définie...
print(df_final[df_final["std"].isna()])
# La Creuse et la Lozère on des déviations non définies, mais je ne sais pas pourquoi
# en recherchant un peu sur internet, il n'y a qu'une seule circonscription pour la Creuse et la Lozère,
# la déviation standard n'est donc pas définie

# je vais donc remplacer la std par 0 quand elle n'est pas définie
df_final.fillna(0., inplace = True)
print(df_final[df_final["std"].isna()])
    

