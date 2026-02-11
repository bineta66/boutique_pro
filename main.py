from db import get_connection
from authentification import login
from datetime import datetime
import mysql.connector

# Connexion à la base
conn, cursor = get_connection()
if conn is None or cursor is None:
    exit()

# Fonctions utilitaires
def saisie_nom_categorie(prompt):
    while True:
        nom = input(f"{prompt}: ").strip()
        if nom.isalpha():
            return nom.capitalize()
        else:
            print("Erreur : doit contenir uniquement des lettres.")

def saisir_prix():
    while True:
        try:
            valeur = int(input("Donner le prix (>=0) : "))
            if valeur >= 0:
                return valeur
            print("Le prix doit être positif.")
        except ValueError:
            print("Veuillez entrer un entier valide.")

def saisir_stock():
    while True:
        try:
            valeur = int(input("Donner le stock (>=0) : "))
            if valeur >= 0:
                return valeur
            print("Le stock doit être positif.")
        except ValueError:
            print("Veuillez entrer un entier valide.")

def saisir_id(prompt="ID : "):
    while True:
        try:
            id_val = int(input(prompt))
            if id_val >= 0:
                return id_val
            print("L'ID doit être positif ou égal à 0.")
        except ValueError:
            print("Veuillez entrer un entier valide.")

# --- Fonctions admin ---
def ajouter_categorie(role):
    if role != "admin":
        print("Accès refusé. Réservé à l'administrateur.")
        return
    nom = saisie_nom_categorie("Nom de la catégorie")                   
    try:
        cursor.execute("INSERT INTO categories (nom_categorie) VALUES (%s)", (nom,))
        conn.commit()
        print(f"Catégorie '{nom}' ajoutée avec succès.")
    except mysql.connector.Error as e:
        print(f"Erreur lors de l'ajout : {e}") 

def afficher_categorie():
    cursor.execute("SELECT * FROM categories")  
    categories = cursor.fetchall()
    if categories:
        print("\n--- Liste des catégories ---")
        for id_, nom in categories:
            print(f"ID: {id_} | {nom}")         
    else:
        print("Aucune catégorie trouvée")    

def ajouter_produit(role):
    if role != "admin":
        print("Accès refusé. Réservé à l'administrateur.")
        return

    afficher_categorie()
    designation = input("Donner le nom du produit : ")
    prix = saisir_prix()
    idcategorie = saisir_id("ID de la catégorie : ")
    stock_initial = saisir_stock()
  
    en_rupture = stock_initial < 5

    cursor.execute("SELECT id FROM categories WHERE id = %s", (idcategorie,))
    if cursor.fetchone() is None:
        print(f"La catégorie avec l'id {idcategorie} n'existe pas.")
        return    

    try:
        cursor.execute(
            "INSERT INTO produits (designation, prix, idcategorie, stock, en_rupture) "
            "VALUES (%s, %s, %s, %s, %s)",
            (designation, prix, idcategorie, stock_initial, en_rupture)
        )
        conn.commit()
        print(f"Produit '{designation}' ajouté avec succès dans la catégorie {idcategorie}. Stock initial : {stock_initial}.")
        print("Statut : En rupture" if en_rupture else "Statut : En stock")
    except mysql.connector.Error as e:
        print(f"Erreur lors de l'ajout : {e}") 

def lister_produits():
    cursor.execute("""
        SELECT p.id, p.designation, p.prix, c.nom_categorie, p.stock, p.en_rupture
        FROM produits p
        JOIN categories c ON p.idcategorie = c.id
    """)
    produits = cursor.fetchall()
    if produits:
        print("\n--- Produits ---")
        for id_, nom, prix, cat, stock, en_r in produits:
            statut = "En rupture" if en_r else "En stock"
            print(f"ID:{id_} - {nom} - Prix:{prix} - Catégorie:{cat} - Stock:{stock} - {statut}")
    else:
        print("Aucun produit trouvé.")

def ajouter_mouvement(role):
    if role != "admin":
        print("Accès refusé. Réservé à l'administrateur.")
        return

    lister_produits()
    id_produit = saisir_id("ID du produit : ")

    cursor.execute("SELECT designation, stock, en_rupture FROM produits WHERE id=%s", (id_produit,))
    produit = cursor.fetchone()
    if not produit:
        print("Produit introuvable !")
        return

    nom_produit, stock_actuel, en_rupture = produit
    type_mouvement = input("Type (ENTREE/SORTIE) : ").upper()
    if type_mouvement not in ("ENTREE", "SORTIE"):
        print("Type incorrect !")
        return

    quantite = saisir_stock()
    if type_mouvement == "ENTREE":
        stock_actuel += quantite
    else:
        if quantite > stock_actuel:
            print("Impossible : stock insuffisant !")
            return
        stock_actuel -= quantite

    en_rupture = stock_actuel < 5

    try:
        cursor.execute(
            "INSERT INTO mouvements (idproduit, type_mouvement, quantite, date_mouvement) "
            "VALUES (%s, %s, %s, %s)",
            (id_produit, type_mouvement, quantite, datetime.now())
        )
        cursor.execute(
            "UPDATE produits SET stock=%s, en_rupture=%s WHERE id=%s",
            (stock_actuel, en_rupture, id_produit)
        )
        conn.commit()
        print(f"Mouvement ajouté : {quantite} {'ajoutées' if type_mouvement=='ENTREE' else 'retirées'} pour '{nom_produit}'")
        print(f"Stock actuel : {stock_actuel} | Statut : {'En rupture' if en_rupture else 'En stock'}")
    except Exception as e:
        print("Erreur :", e)

def afficher_historique():
    cursor.execute("""
        SELECT h.id, p.designation, h.type_mouvement, h.quantite,
               h.stock_actuel, h.en_rupture, h.date_mouvement
        FROM historique h
        JOIN produits p ON h.idproduit = p.id
        ORDER BY h.date_mouvement DESC
    """)
    mouvements = cursor.fetchall()
    if not mouvements:
        print("Aucun mouvement enregistré.")
        return
    print("\n--- Historique des mouvements ---")
    for m in mouvements:
        id_, nom_produit, type_mouvement, quantite, stock, en_rupture, date_mvt = m
        statut = "En rupture" if en_rupture else "En stock"
        print(f"[{date_mvt}] Produit: {nom_produit} | Type: {type_mouvement} | Quantité: {quantite} - Stock actuel: {stock} - Statut: {statut}")

def afficher_alertes():
    cursor.execute("SELECT designation, stock FROM produits WHERE stock < 5")
    alertes = cursor.fetchall()
    if not alertes:
        print("Aucun produit en rupture.")
        return
    print("\n--- Produits en alerte (stock < 5) ---")
    for produit, stock in alertes:
        print(f"{produit} - Stock actuel : {stock} - Statut : En rupture")

# --- Menu ---
def menu(username, role):
    while True:
        print("\n====== Menu principal ======")
        print(f"Bienvenue : {username} ")

        if role == "admin":
            print("1. Ajouter catégorie")
            print("2. Ajouter produit")
            print("3. Mouvement")
            print("4. Historique")
            print("5. Alertes")
            print("6.Lister categories")
            print("7.Lister produits")
            print("8. Déconnexion")
        else:
            print("1. Lister produits")
            print("2.Lister catégories")
            print("3. Alertes")
            print("4. Déconnexion")

        choix = input("Choix : ")

        if role == "admin":
            if choix == "1": 
                ajouter_categorie(role)
            elif choix == "2":
                 ajouter_produit(role)
            elif choix == "3": 
                ajouter_mouvement(role)
            elif choix == "4":
                 afficher_historique()
            elif choix == "5": 
                afficher_alertes()
            elif choix == "6":
                afficher_categorie()
            elif choix == "7":
                 lister_produits()
            elif choix == "8":
                    break     
            else: print("Choix invalide.")
        else:
            if choix == "1": 
                lister_produits()
            elif choix == "2": 
                lister_produits()
            elif choix == "3": 
                afficher_alertes()
            elif choix == "4":
                break    
            else: print("Choix invalide.")

# --- Programme principal ---
if __name__ == "__main__":
    # Crée Bineta (admin) et Atou (user)
    username, role = login()  

    if role:
        menu(username, role)
    else:
        print("Fin du programme.")

    cursor.close()
    conn.close()
