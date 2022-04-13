#!/usr/bin/python3

# Importation des modules.
import shutil
from pathlib import Path

# Définition de variable globale.
limite = 0.85

# Évaluation de racine de disque.
# https://docs.python.org/fr/3/library/pathlib.html?highlight=cwd#pathlib.Path.cwd
cwd = Path.cwd()
root = cwd.root or cwd.drive

# Recherche des détails du disque.
# https://docs.python.org/fr/3/library/shutil.html?highlight=usage#shutil.disk_usage
usage = shutil.disk_usage(root)

# Calcul d'ultilisation de disque en pourcentage.
p_utilise = usage.used / usage.total
# Sortie définie selon pourcentage et limite.
if p_utilise > limite:
    print("Trop de vidéos !")
else:
    print("Pas assez de vidéos !")
