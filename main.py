from db import get_connection
import mysql.connector

from datetime import datetime  
# Connexion
conn, cursor = get_connection()
if conn is None or cursor is None:
    exit()

# fonction  sur le nom categorie pour qu' il saisie seulement des llettres 
def saisie_nom_categorie(prompt):
    while True:
        nom = input(f"{prompt}: ").strip()
        if nom.isalpha():
            return nom.capitalize()
        else:
            print("Erreur : doit contenir uniquement des lettres.")
# controler le saisie sur le prix et stock pour que il ne soient pas negatifs ou null
def saisir_prix_stock():
    while True:
        try:
            valeur = int(input("Donner le prix ou stock (>=0) : "))
            if valeur >= 0:
                return valeur
            else:
                print("Le prix ou stock doit être positif.")
        except ValueError:
            print("Veuillez entrer un entier valide.")
# controler le saise sur les id
def saisir_id(prompt="ID : "):
    while True:
        try:
            id_val = int(input(prompt))
            if id_val >= 0:
                return id_val
            else:
                print("L'ID doit être positif ou égal à 0.")
        except ValueError:
            print("Veuillez entrer un entier valide.")
# fonction ajouter catégorie

def ajouter_categorie():
    nom = saisie_nom_categorie("Nom de la catégorie")                   
    try:
        cursor.execute("INSERT INTO categories (nom_categorie) VALUES (%s)", (nom,))
        conn.commit()
        print(f"Catégorie '{nom}' ajoutée avec succès.")
    except mysql.connector.Error as e:
        print(f"Erreur lors de l'ajout : {e}") 
# fonction afficher categorie
def afficher_categorie():
    cursor.execute("SELECT * FROM categories")  
    categories = cursor.fetchall()
    if categories:
        print("\n--- Liste des catégories ---")
        for id_, nom in categories:
            print(f"ID: {id_} | {nom}")         
    else:
        print("Aucune catégorie trouvée")    


def ajouter_produit():
    designation = input("Donner le nom du produit : ")
    prix = saisir_prix_stock()
    idcategorie = saisir_id("ID de la catégorie : ")
    stock_initial = saisir_prix_stock()

  
    if stock_initial < 5:
        en_rupture = True
    else:
        en_rupture = False    

   
    cursor.execute("SELECT id FROM categories WHERE id = %s", (idcategorie,))
    categorie = cursor.fetchone()
    if categorie is None:
        print(f"La catégorie avec l'id {idcategorie} n'existe pas.")
        return    

    try:
        sql = """
        INSERT INTO produits (designation, prix, idcategorie, stock, en_rupture)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (designation, prix, idcategorie, stock_initial, en_rupture))
        conn.commit()
        print(f"Produit '{designation}' ajouté avec succès dans la catégorie {idcategorie}. "
              f"Stock initial : {stock_initial}.")

            #  pour afficher  en rupture  en utliser statut qui remplace true or false par en rupture et en stock
        if en_rupture:
            print("Statut : En rupture")
        else:
            print("Statut : En stock")

    except mysql.connector.Error as e:
        print(f"Erreur lors de l'ajout : {e}") 


def lister_produits():
    cursor.execute("""
        SELECT p.id, p.designation, p.prix, c.nom_categorie, p.stock, p.en_rupture
        FROM produits p
        JOIN categories c ON p.idcategorie = c.id
    """)
    produit = cursor.fetchall()
    if produit:
        print("\n--- Produits ---")
        for id_, nom, prix, cat, stock, en_r in produit:
            if en_rupture:
                     print(f"Stock actuel : {stock_actuel} | Statut : En rupture")
            else:
                    print(f"Stock actuel : {stock_actuel} | Statut : En stock")
            print(f"ID:{id_} - {nom} - Prix:{prix} - Catégorie:{cat} - Stock:{stock} - {statut}")
    else:
        print("Aucun produit trouvé.")


def ajouter_mouvement():
    id_produit = int(input("ID du produit : "))

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

    quantite = int(input("Quantité : "))
    if quantite <= 0:
        print("La quantité doit être positive !")
        return

    # Calcul du nouveau stock
    if type_mouvement == "ENTREE":
        stock_actuel += quantite
    else:
        stock_actuel -= quantite
        if stock_actuel < 0:
            print("Impossible : stock insuffisant !")
            return

    # Déterminer le statut
    en_rupture = stock_actuel < 5

    try:
        # Ajouter le mouvement
        cursor.execute("""
            INSERT INTO mouvements (idproduit, type_mouvement, quantite, date_mouvement)
            VALUES (%s, %s, %s, %s)
        """, (id_produit, type_mouvement, quantite, datetime.now()))

        # Mettre à jour le stock et le statut
        cursor.execute("""
            UPDATE produits
            SET stock=%s, en_rupture=%s
            WHERE id=%s
        """, (stock_actuel, en_rupture, id_produit))

        conn.commit()

        # Affichage simple
        if type_mouvement == "ENTREE":
            print(f"Mouvement ajouté : {quantite} ajoutées pour '{nom_produit}'")
        else:
            print(f"Mouvement ajouté : {quantite} retirées pour '{nom_produit}'")

        if en_rupture:
            print(f"Stock actuel : {stock_actuel} | Statut : En rupture")
        else:
            print(f"Stock actuel : {stock_actuel} | Statut : En stock")

    except Exception as e:
        print("Erreur :", e)


def afficher_historique():
    try:
        # On récupère les mouvements avec le nom du produit
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
            print(f"[{date_mvt}] Produit: {nom_produit} | Type: {type_mouvement} | "
                  f"Quantité: {quantite} - Stock actuel: {stock} - Statut: {statut}")
    except Exception as e:
        print("Erreur lors de l'affichage de l'historique :", e)

def afficher_alertes():
    cursor.execute("""
        SELECT designation, stock
        FROM produits
        WHERE stock < 5
    """)
    alertes = cursor.fetchall()
    
    if not alertes:
        print("Aucun produit en rupture.")
        return
    
    print("\n--- Produits en alerte (stock < 5) ---")
    for produit, stock in alertes:
        print(f"{produit} - Stock actuel : {stock} - Statut : En rupture")

def menu():
    while True:
        print("\n====== Menu principal ======")
        print("1. Ajouter catégorie")
        print("2. Lister catégories")
        print("3. Ajouter produit")
        print("4. Ajouter mouvement")
        print("5. Liste produits")
        print("6. Historique")
        print("7. Produits en rupture")
        print("8. Quitter")

        choix = input("Choix : ")

        if choix == "1":
            ajouter_categorie()
        elif choix == "2":
            afficher_categorie()
        elif choix == "3":
            ajouter_produit()
        elif choix == "4":
            ajouter_mouvement()
        elif choix == "5":
            lister_produits()
        elif choix == "6":
            afficher_historique()
        elif choix == "7":
            afficher_alertes()
        elif choix == "8":
            print("Au revoir !")
            break
        else:
            print("Choix invalide. Veuillez sélectionner un numéro entre 1 et 8.")




if __name__ == "__main__":
    menu()
    cursor.close()
    conn.close()