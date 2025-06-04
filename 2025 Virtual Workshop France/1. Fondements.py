"""
Démonstration de Kinetics Toolkit - 1. Fondements.

Ce script Python couvre les fondements des TimeSeries sous Kinetics Toolkit.

Il est écrit de façon à être exécuté cellule par cellule, par
exemple dans Spyder en utilisant le bouton "Run Cell", ou CTRL+Enter
(CMD+Enter sur Mac).

Félix Chénier, 2025

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import kineticstoolkit.lab as ktk

# %% Créer une TimeSeries

# Créer la TimeSeries
ts = ktk.TimeSeries()

# Afficher le contenu de la TimeSeries dans la console
ts

# %% Obtenir de l'aide

"""
- Obtenir de l'aide sur la TimeSeries
    - Entrer ts dans le panneau d'aide de Spyder
    - Entrer ts? dans la console

- Obtenir de l'aide sur les méthodes de la TimeSeries
    - Lister les méthodes disponibles: dir(ts)
    - Entrer ts.NOM_DE_LA_METHODE dans le panneau d'aide de Spyder
    - Entrer ts.NOM_DE_LA_METHODE? dans la console
"""

# %% Ajouter des données dans notre TimeSeries

ts.time = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]

# On peut assigner des données directement à la propriété data
ts.data["Sinus"] = np.sin(ts.time)

# ou utiliser add_data, ce qui applique des tests supplémentaires (overwrite,
# vérification des tailles, etc.)
ts = ts.add_data("Cosinus", np.cos(ts.time))

ts

# %% Ajouter des données multidimensionnelles

ts = ts.add_data("Random", np.random.rand(13, 3) / 4)

ts.data

# %% Afficher la TimeSeries sur un graphique

ts.plot()

# Si le graphique ne s'affiche pas dans une fenêtre séparée, consulter:
# https://kineticstoolkit.uqam.ca/doc/getting_started_configuring_spyder.html
#
# ou taper "%matplotlib qt" dans la console

# %% Afficher seulement une partie des données

ts.plot(["Sinus"])

# %% Utiliser les styles de Matplotlib

ts.plot(["Sinus"], ".-")

# %% Rééchantillonner à 10 Hz

plt.figure()

plt.subplot(4, 1, 1)
ts.plot([], ".-")

plt.subplot(4, 1, 2)
ts.resample(10).plot([], ".-")

plt.subplot(4, 1, 3)
ts.resample(10, kind="nearest").plot([], ".-")

plt.subplot(4, 1, 4)
ts.resample(10, kind="cubic").plot([], ".-")

# %% Ajouter des événements (par commande)

# Utiliser la version "spline cubique" pour le reste de la démonstration
ts = ts.resample(10, kind="cubic")

# Ajouter des événements
ts = ts.add_event(1.5, "start")
ts = ts.add_event(2.0, "event")
ts = ts.add_event(3.0, "event")
ts = ts.add_event(4.0, "event")
ts = ts.add_event(10.0, "stop")

ts

# %% Afficher la TimeSeries avec les événements

ts.plot()

# %% Modifier les événements

"""
Modifier les événements pour que les événements "event" soient au minimum des
courbes "Sinus" et "Cosinus".
"""

ts = ts.ui_edit_events()

# %% Utiliser les événements pour extraire de l'information de la TimeSeries

print("Index le plus près du premier 'event':", ts.get_index_at_event("event"))
print("Index après le premier 'event':", ts.get_index_after_event("event"))
print("Index avant le premier 'event':", ts.get_index_before_event("event"))

# %% ...

print("Index le plus près du 1e 'event':", ts.get_index_at_event("event", 0))
print("Index le plus près du 2e 'event':", ts.get_index_at_event("event", 1))
print("Index le plus près du 3e 'event':", ts.get_index_at_event("event", 2))

# %% Utiliser les événements pour extraire des "sous"-TimeSeries

ts_cycle_cos = ts.get_ts_between_events("event", "event", 0, 2)

ts_cycle_cos.plot()

# %% Sauvegarder et recharger des données

ktk.save("sauvegarde.ktk.zip", ts_cycle_cos)

new_ts = ktk.load("sauvegarde.ktk.zip")

new_ts.plot()

# %% Exporter vers Pandas, puis vers Excel

df = ts_cycle_cos.to_dataframe()
df.to_excel("export.xlsx")

# Pandas pourrait avoir besoin du module openpyxl qui n'est pas installé par
# défaut par Pandas.
# conda install -c conda-forge openpyxl

# %% Exporter la liste d'events vers Excel

df = pd.DataFrame(ts_cycle_cos.events)
df.to_excel("events.xlsx")
