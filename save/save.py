import json

# fonction pour sauvegarder les données
def sauvegarder_donnees(donnees, fichier):
    with open(fichier, 'w') as f:
        json.dump(donnees, f)

# fonction pour charger les données
def charger_donnees(fichier):
    with open(fichier) as f:
        donnees = json.load(f)
    return donnees

# importer la sauvegarde
import os

fichier = "donnees.json"
if os.path.isfile(fichier):
    donnees = charger_donnees(fichier)
    print("Sauvegarde trouvée. Les données ont été chargées.")
else:
    donnees = {"historique": ["commande1","commande2"], "conversation": ["question1","reponse1","question2","reponse2"]}
    print("Aucune sauvegarde trouvée. Des données vides ont été initialisées.")

# sauvegarder
sauvegarder_donnees(donnees, fichier)

# historique = donnees["historique"]
# for x in range(len(historique)):
#     a = historique[x]
#     print(a["command"])