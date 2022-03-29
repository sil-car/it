#!/usr/bin/python3

# Importer des modules dont nous avons besoin
from subprocess import PIPE, run
from sys import platform

# Définition des variables globales
NOM_DE_PROCESSUS = "wuauserv"
NOMBRE_PREVU = 1

# déteriminer le genre de l'OS et définir `shell_command`.
if platform == 'darwin':
    print("ATTENTION: Ce script n'est pas encore vérifié sur MacOS.")
if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
    shell_command = "pgrep " + NOM_DE_PROCESSUS + " -c"
elif platform == 'win32':
    shell_command = "sc query " + NOM_DE_PROCESSUS + " | find \"RUNNING\" /c"
else:
    print(f"Ce script n'est pas compatible avec la plateforme \"{platform}\".")
    exit(1)

# Note: this does not throw error on non-zero exit code.
# Cette commande nous donnera combien des processus sont en cours d'execution en chiffres.
completed_process = run(shell_command,  check=False, stdout=PIPE, shell=True)
if completed_process.returncode == 0:
  sortie_comme_string = completed_process.stdout.decode()
  sortie_sans_fins_de_ligne = sortie_comme_string.strip()
  nombre_des_procs = int(sortie_sans_fins_de_ligne)
else:
  nombre_des_procs = 0

if nombre_des_procs != NOMBRE_PREVU:
  print(f'Nombre inattendu de processus trouvé: {nombre_des_procs}')
else:
  print("Processus trouvé!")	
