README – Application de Gestion de Stock Boutique
Présentation du projet

Cette application est un programme en Python connecté à une base de données MySQL.
Elle permet de gérer les catégories, 
les produits et les mouvements de stock (entrées et sorties).

Le système met automatiquement à jour :

la quantité en stock

le statut du produit (En stock / En rupture)

l’historique des opérations



Technologies utilisées

Python 3

MySQL

mysql-connector-python

Terminal / VS Code

Structure de la base de données
Table categories
Champ	Type	Description
id	int	Identifiant
nom_categorie	varchar	Nom de la catégorie


Table produits
Champ	Type	Description
id	int	Identifiant
designation	varchar	Nom du produit
prix	int	Prix du produit
idcategorie	int	Catégorie associée
stock	int	Quantité disponible
en_rupture	boolean	Indique si le stock < 5


Table mouvements
Champ	Type
id	int
idproduit	int
type_mouvement	ENTREE / SORTIE
quantite	int
date_mouvement	datetime
Fonctionnalités principales
Gestion des catégories

Ajouter une catégorie

Lister les catégories

Gestion des produits

Ajouter un produit

Vérification que la catégorie existe

Enregistrement du stock initial

Détermination automatique du statut :

stock < 5 → En rupture

sinon → En stock

Mouvements de stock

L’utilisateur peut :

Ajouter du stock (ENTREE)

Retirer du stock (SORTIE)

Chaque opération :

✔ ajoute une ligne dans mouvements
✔ met à jour la quantité dans produits
✔ recalcul le statut en_rupture

Sécurité de gestion

Le programme vérifie :

si le produit existe

si la quantité est valide

si le stock est suffisant avant une sortie

Logique métier importante

Après chaque mouvement :

si stock < 5
    en_rupture = True
sinon
    en_rupture = False


Cela permet d’alerter rapidement sur les produits presque épuisés.

Lancement du programme
1. Activer l’environnement virtuel
source venv/bin/activate

2. Lancer l’application
python main.py

Menu principal
1. Ajouter catégorie
2. Lister catégories
3. Ajouter produit
4. Lister produits
5. Ajouter mouvement
6. Quitter

📊 Exemple d’utilisation

Ajout d’une entrée de stock :

ID du produit : 1
Type : ENTREE
Quantité : 10


Le programme :

ajoute dans mouvements

augmente le stock

affiche le nouveau statut

Organisation du projet
boutique_pro/
│
├── main.py          → menu et fonctions
├── db.py            → connexion MySQL
├── README.md
└── dump.sql         → structure de la base

 Objectifs pédagogiques atteints

✔ Utilisation de Python avec base relationnelle
✔ Requêtes SQL (INSERT, SELECT, UPDATE)
✔ Gestion d’erreurs
✔ Séparation connexion / logique
✔ Mise en place de règles métier
✔ Historisation des actions

Améliorations possibles (futur)

Interface graphique

Recherche de produits

Statistiques

authentification admin

export PDF / Excel
