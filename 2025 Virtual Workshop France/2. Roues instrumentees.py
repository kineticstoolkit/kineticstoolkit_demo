"""
Démonstration de Kinetics Toolkit - 2. Roues instrumentées

Ce script Python couvre l'analyse spatiotemporelle et cinétique à l'aide de
roues instrumentées de fauteuil roulant.

Il est écrit de façon à être exécuté cellule par cellule, par
exemple dans Spyder en utilisant le bouton "Run Cell", ou CTRL+Enter
(CMD+Enter sur Mac).

Félix Chénier, 2025

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import kineticstoolkit.lab as ktk

# KTK vise à être le plus générique possible, alors que le traitement de roues
# instrumentées est très spécifique à un domaine de recherche particulier.
# Ainsi, on utilise l'extension kineticstoolkit_pushrimkinetics disponible ici:
#
#   https://github.com/kineticstoolkit/kineticstoolkit_pushrimkinetics
#
# Il s'agit simplement de télécharger ce module supplémentaire et de le mettre
# dans le même dossier que notre code. C'est déjà fait pour cette
# démonstration.
import kineticstoolkit_pushrimkinetics as pk

# %% Lire un fichier CSV généré par la roue SmartWheel

ts = pk.read_smartwheel("pushrimkinetics_offsets_propulsion.csv")

ts.plot()

# %% Afficher seulement les forces et moments
plt.figure()

plt.subplot(2, 1, 1)
ts.plot("Forces")

plt.subplot(2, 1, 2)
ts.plot("Moments")

# %% Enlever les offsets dûs au poids de la main courante

ts = pk.remove_offsets(ts)

plt.figure()

plt.subplot(2, 1, 1)
ts.plot("Forces")

plt.subplot(2, 1, 2)
ts.plot("Moments")

# %% Calculer la force totale Ftot

ts = ts.add_data("Ftot", np.sqrt(np.sum(ts.data["Forces"] ** 2, axis=1)))

ts.plot(["Forces", "Ftot"])

# %% Calculer la vitesse angulaire et la puissance

ts = pk.calculate_velocity(ts)
ts = pk.calculate_power(ts)

ts.plot(["Moments", "Velocity", "Power"])

# %% Isoler les poussées (manuellement)

ts = ts.ui_edit_events(["push", "recovery"], ["Forces", "Ftot"])

# %% Isoler les poussées (automatiquement)

ts.events = []  # Effacer les événements de l'étape précédente

# Faire un premier travail automatique
ts = ktk.cycles.detect_cycles(
    ts,
    "Ftot",
    event_names=["push", "recovery"],
    thresholds=[5.0, 2.0],
    min_durations=[0.1, 0.1],
    min_peak_heights=[25.0, -np.Inf],
)

# Inspecter et corriger au besoin
ts = ts.ui_edit_events(["push", "recovery"], ["Forces", "Ftot"])

# %% Faire une analyse spatiotemporelle et cinétique poussée par poussée

n_cycles = ts.count_events("push")

all_analyses = []  # Liste de toutes les analyses, cycle par cycle

for i_cycle in range(n_cycles):

    # Initialiser un dictionnaire pour l'analyse de ce cycle
    this_analysis = {}

    # Isoler la poussée seulement
    ts_push = ts.get_ts_between_events("push", "recovery", i_cycle, i_cycle)

    # Isoler le recouvrement seulement
    ts_recov = ts.get_ts_between_events("recovery", "_", i_cycle, i_cycle)

    # Isoler le cycle complet
    ts_cycle = ts.get_ts_between_events("push", "_", i_cycle, i_cycle)

    # Analyse spatiotemporelle
    this_analysis["Push Time (s)"] = ts_push.time[-1] - ts_push.time[0]
    this_analysis["Recovery Time (s)"] = ts_recov.time[-1] - ts_recov.time[0]
    this_analysis["Cycle Time (s)"] = ts_cycle.time[-1] - ts_cycle.time[0]

    this_analysis["Push Angle (deg)"] = np.rad2deg(
        ts_push.data["Angle"][-1] - ts_push.data["Angle"][0]
    )

    this_analysis["Mean Speed (deg/s)"] = np.mean(
        np.rad2deg(ts_push.data["Velocity"])
    )

    # Analyse cinétique
    this_analysis["Mean Total Force (N)"] = np.mean(ts_push.data["Ftot"])
    this_analysis["Peak Total Force (N)"] = np.max(ts_push.data["Ftot"])

    this_analysis["Mean Propulsion Moment (Nm)"] = np.mean(
        ts_push.data["Moments"][:, 2]
    )
    this_analysis["Peak Propulsion Moment (Nm)"] = np.max(
        ts_push.data["Moments"][:, 2]
    )

    this_analysis["Mean Power (W)"] = np.mean(ts_push.data["Power"])

    # Ajouter cette analyse à la liste et passer à la suiante
    all_analyses.append(this_analysis)


all_analyses

# %% Combiner dans un DataFrame et exporter vers Excel

df = pd.DataFrame(all_analyses)

df.to_excel("wheelchair_analysis.xlsx")

# %% AUTRE ANALYSE - PATRON CINÉMATIQUE MOYEN

# Ici, on isole les cycles de propulsion les plus répétables, pour afficher
# le cycle de propulsion moyen sur une courbe.

# %% Normaliser les poussées de 0 à 100%

ts_normalized = ktk.cycles.time_normalize(ts, "push", "recovery")

ts_normalized.plot(["Forces", "Ftot", "Moments"])

# %% Empiler les poussées dans un seul array

stacked = ktk.cycles.stack(ts_normalized)

stacked

# %% Afficher les poussées une à une

plt.figure()

plt.subplot(1, 2, 1)
plt.title("Ftot")

for i_cycle in range(n_cycles):
    plt.plot(stacked["Ftot"][i_cycle])

plt.subplot(1, 2, 2)
plt.title("Mz")

for i_cycle in range(n_cycles):
    plt.plot(stacked["Moments"][i_cycle, :, 2])


# %% Déterminer les poussées les plus répétables

repeatable_indexes = ktk.cycles.most_repeatable_cycles(stacked["Ftot"])

repeatable_indexes

# %% Afficher seulement les 20 poussées les plus répétables

n_to_keep = 20

plt.figure()

plt.subplot(1, 2, 1)
plt.title("Ftot")

for i_cycle in repeatable_indexes[0:n_to_keep]:
    plt.plot(stacked["Ftot"][i_cycle])

plt.subplot(1, 2, 2)
plt.title("Mz")

for i_cycle in repeatable_indexes[0:n_to_keep]:
    plt.plot(stacked["Moments"][i_cycle, :, 2])

# %% Afficher un graphique de moyenne ± écart-type

n_to_keep = 20

Ftot = stacked["Ftot"][repeatable_indexes[0:n_to_keep]]
Mz = stacked["Moments"][repeatable_indexes[0:n_to_keep], :, 2]


plt.figure()

plt.subplot(1, 2, 1)
plt.title("Ftot")

plt.fill_between(
    np.arange(100),
    Ftot.mean(axis=0) - Ftot.std(axis=0),
    Ftot.mean(axis=0) + Ftot.std(axis=0),
    alpha=0.2
)
plt.plot(Ftot.mean(axis=0),'r')


plt.subplot(1, 2, 2)
plt.title("Mz")

plt.fill_between(
    np.arange(100),
    Mz.mean(axis=0) - Mz.std(axis=0),
    Mz.mean(axis=0) + Mz.std(axis=0),
    color='b',
    alpha=0.2
)
plt.plot(Mz.mean(axis=0),'b')

