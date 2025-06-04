"""
Démonstration de Kinetics Toolkit - 3. Cinématique

Ce script Python couvre la visualisation et le traitement de marqueurs
réfléchissants pour déterminer les angles articulaires du coude.

Il reprend le tutorial à cette adresse:
    https://kineticstoolkit.uqam.ca/doc/kinematics_joint_angles.html

Il est écrit de façon à être exécuté cellule par cellule, par
exemple dans Spyder en utilisant le bouton "Run Cell", ou CTRL+Enter
(CMD+Enter sur Mac).

Félix Chénier, 2025

"""

import matplotlib.pyplot as plt

import kineticstoolkit.lab as ktk

# %% Fondements de géométrie: série de vecteurs

vector_series = ktk.geometry.create_vector_series(
    x=[1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.4, 1.3, 1.2, 1.1],
    z=[1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9],
)

vector_series

# %% Fondements de géométrie: série de points

point_series = ktk.geometry.create_point_series(
    x=[1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.4, 1.3, 1.2, 1.1],
    z=[1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9],
)

point_series

# %% Visualiser des points

ts = ktk.TimeSeries(time=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
ts = ts.add_data("Point", point_series)

p = ktk.Player(ts)

# %% Fondements de géométrie: série de transformations rigides

# Rotation de 0 à 90 degrés autour de l'axe z
transform_series = ktk.geometry.create_transform_series(
    angles=[0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0],
    seq="z",
    degrees=True,
)

ts = ts.add_data("RotationZ", transform_series)

p = ktk.Player(ts)

# %% Fondements de géométrie: série de transformations rigides (suite)

# Création d'une matrice de transformation rigide à partir de points

transform_series = ktk.geometry.create_transform_series(
    x=vector_series, xy=[[0.0, 1.0, 0.0, 0.0]]
)

ts = ktk.TimeSeries(time=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
ts = ts.add_data("Point", point_series)
ts = ts.add_data("Frame", transform_series)

p = ktk.Player(ts)

# %% L'EXEMPLE COMMENCE ICI.

# Charger un fichier c3d (propulsion d'un fauteuil de course sur rouleau)

file = ktk.doc.download("kinematics_racing_full.c3d")

file_contents = ktk.read_c3d(file)

file_contents

# %% Visualiser les points

points = file_contents["Points"]

p = ktk.Player(points)

# %% Relier les points pour faciliter la visualisation

interconnections = {
    "ArmR": {
        "Color": [1, 0.25, 0],
        "Links": [
            [
                "AcromionR",
                "LateralEpicondyleR",
                "MedialEpicondyleR",
                "AcromionR",
            ]
        ],
    },
    "ForearmR": {
        "Color": [1, 0.5, 0],
        "Links": [
            ["MedialEpicondyleR", "UlnarStyloidR"],
            ["LateralEpicondyleR", "RadialStyloidR"],
            ["UlnarStyloidR", "RadialStyloidR"],
        ],
    },
}

p = ktk.Player(points, interconnections=interconnections)

# %% Créer le système d'axes du bras, selon l'ISB

# Origine = Articulation gléno-humérale (approximée ici par l'acromion)
origin = points.data["AcromionR"]

# Axe Y: la ligne entre l'articulation gléno-humérale et le milieu du coude
# pointant vers l'articulation gléno-humérale
y = points.data["AcromionR"] - 0.5 * (
    points.data["LateralEpicondyleR"] + points.data["MedialEpicondyleR"]
)

# Axe X: perpendiculaire au plan formé par l'articulation gléno-humérale et
# les deux épicondyle, pointant vers l'avant.
yz = points.data["LateralEpicondyleR"] - points.data["MedialEpicondyleR"]

arm = ktk.geometry.create_transform_series(y=y, yz=yz, positions=origin)

# %% Créer une TimeSeries pour les systèmes d'axe

transforms = ktk.TimeSeries(time=points.time)
transforms = transforms.add_data("ArmR", arm)

p = ktk.Player(points, transforms, interconnections=interconnections)

# %% Créer le système d'axe de l'avant-bras, selon l'ISB

# Origine = Processus styloïde ulnaire
origin = points.data["UlnarStyloidR"]

# Axe Y: la ligne entre le processus styloïde ulnaire et le milieu du coude,
# pointant vers le milieu du coude.
y = (
    0.5
    * (points.data["LateralEpicondyleR"] + points.data["MedialEpicondyleR"])
    - points.data["UlnarStyloidR"]
)

# Axe X: perpendiculaire au plan formé par les deux processus styloïdes et le
# milieu du coude.
yz = points.data["RadialStyloidR"] - points.data["UlnarStyloidR"]

forearm = ktk.geometry.create_transform_series(positions=origin, y=y, yz=yz)

transforms = transforms.add_data("ForearmR", forearm)

p = ktk.Player(points, transforms, interconnections=interconnections)

# %% Calculer la série de transformations rigides entre arm et forearm

# Ce qui revient à exprimer le système d'axe "ForearmR" en référence au
# système d'axe "ArmR"

arm_to_forearm = ktk.geometry.get_local_coordinates(
    transforms.data["ForearmR"], transforms.data["ArmR"]
)

arm_to_forearm

# %% Extraire la série d'angles d'Euler permettant de créer arm_to_forearm

euler_angles = ktk.geometry.get_angles(arm_to_forearm, "ZXY", degrees=True)

plt.plot(euler_angles)

# %% Créer une TimeSeries pour documenter quel angle est quoi
angles = ktk.TimeSeries(time=points.time)
angles = angles.add_data("Flexion", euler_angles[:, 0])
angles = angles.add_data("Carrying angle", euler_angles[:, 1])
angles = angles.add_data("Pronation", euler_angles[:, 2])

angles.plot()
