#!/usr/bin/python3

# Importer des modules dont nous avons besoin
import sys
import time
from pathlib import Path
from datetime import datetime,timezone,timedelta

# définition variable globale
JOUR_EN_SECONDS = 24 * 60 * 60
OFFSET = 4 * JOUR_EN_SECONDS

# Créer une date OFFSET avant ce moment-ci
exemple_date = datetime.fromtimestamp(time.time() - OFFSET, timezone(timedelta(hours=1)))

trouve = 0
# Path va aller selon la plateforme utilisée
# Ce fichier est un journal qui est comme un journal Apache
chemin_de_fichier = Path("./datafiles/log_file")

if chemin_de_fichier.exists():
    with chemin_de_fichier.open("r", encoding="UTF-8") as log_file:
        lignes = log_file.readlines()
        for ligne in lignes:
            ligne_crue = ligne.strip()

            # Separate out date from rest of line
            substring_debut = ligne_crue.find('[')
            substring_fin = ligne_crue.find(']')
            date_de_ligne = ligne_crue[(substring_debut+1):(substring_fin)]

            # Turn string into datetime object
            journal_date = datetime.strptime(date_de_ligne, "%d/%b/%Y:%H:%M:%S %z")

            if journal_date > exemple_date:
                trouve = 1
else:
    print("Erreur: opening file" + str(chemin_de_fichier), file=sys.stderr)
    exit(1)


if trouve:
    print(f"Il y a du contentu du journal trouvé depuis {exemple_date}")
else:
    print(f"Aucun contenu du journal trouvé depuis {exemple_date}")
