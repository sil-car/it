#!/usr/bin/python3

# Verifier que un hôte est disponible.

# Importer des modules dont nous avons besoin
import subprocess
import sys

# définition variable globale
MAX_ATTENTE = '3'

# définir l'adresse IP à laquelle on va envoyer les paquets
adresse = '127.0.0.1' # par défault
if len(sys.argv) > 1:
    adresse = sys.argv[1]

# déteriminer le genre de l'OS et définir `shell_command`.
if sys.platform == 'darwin':
    print("ATTENTION: Ce script n'est pas encore vérifié sur MacOS.")
if sys.platform == 'linux' or sys.platform == 'linux2' or sys.platform == 'darwin':
    shell_command = f"ping -w {MAX_ATTENTE} {adresse}"
elif sys.platform == 'win32':
    shell_command = f"ping -w {MAX_ATTENTE} {adresse}"
    # shell_command = f"ping /w {MAX_ATTENTE} {adresse}"
else:
    print(f"Ce script n'est pas compatible avec la plateforme \"{platform}\".")
    exit(1)

# Executer la commande shell
completed_process = subprocess.run(
    shell_command,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    shell=True,
)

# Set status depending on command returncode.
if completed_process.returncode == 0:
    statut = 'active'
else:
    statut = 'hors service'

# Afficher les resultats.
print(f'Hôte "{adresse}" est {statut}.')
