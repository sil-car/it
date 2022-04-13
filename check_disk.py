# Importation des modules.
import subprocess
import shutil
from pathlib import Path

# Définition de variable globale.
limite = 0.85

# Évaluation de racine de disque.
cwd = Path(".").resolve()
root = cwd.root or cwd.drive

# Recherche des détails du disque.
usage = shutil.disk_usage(root)

# Calcul d'ultilisation de disque en pourcentage.
p_utilise = usage.used / usage.total
# Sortie définie selon pourcentage et limite.
if p_utilise > limite:
    print("Trop de vidéos !")
else:
    print("Pas assez de vidéos !")