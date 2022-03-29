#!/usr/bin/python3

# Developpé par Brian Yee et Nate Marti.

# Importer des modules dont nous avons besoin
from subprocess import check_output
from sys import platform

# définition variable globale
LIMITE = 0.85

# déteriminer le genre de l'OS et définir `shell_command`.
if platform == 'darwin':
    print("ATTENTION: Ce script n'est pas encore vérifié sur MacOS.")
if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
    shell_command = "lsblk --bytes --output=FSAVAIL,MOUNTPOINT,SIZE | grep \"\s/\s\""
elif platform == 'win32':
    shell_command = "wmic logicaldisk GET Name,Size,FreeSpace | find /i \"C:\""
else:
    print(f"Ce script n'est pas compatible avec la plateforme \"{platform}\".")
    exit(1)

# Executer la commande shell et parser ce qui sort
sortie_comme_octets = check_output(shell_command, shell=True)
sortie_comme_string = sortie_comme_octets.decode()
sortie_sans_fins_de_ligne = sortie_comme_string.strip()
sortie_parsee = sortie_sans_fins_de_ligne.split()

# Définir variables pour l'analyse
espace_libre = int(sortie_parsee[0]) # convert to a number
nom_de_disque = sortie_parsee[1]
capacite = int(sortie_parsee[2]) # convert to a number

# Calculer le pourcentage d'utilisation
pourcentage_utilise = (capacite - espace_libre) / capacite
pourcentage = "{:.2%}".format(pourcentage_utilise)

# Afficher les resultats
print(f'Le disque {nom_de_disque} a la capacité de {capacite} et il a l\'espace libre de {espace_libre}')
print(f'Ça fait {pourcentage}')

if (pourcentage_utilise > LIMITE):
    print('Le disque s\'approche sa capacité')
else:
    print('Le disque est OK')
