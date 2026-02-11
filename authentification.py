import hashlib
from getpass import getpass
from db import get_connection


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()



def login():
    conn, cursor = get_connection()

    try:
        while True:
            username = input("Nom utilisateur : ")

            cursor.execute("SELECT password, role FROM utilisateurs WHERE username=%s", (username,))
            user = cursor.fetchone()

            if user:
                break
            else:
                print("Utilisateur inexistant. Réessayez.\n")

        tentatives = 3
        while tentatives > 0:
            password = getpass("Mot de passe : ")
            password_hash = hash_password(password)

            if password_hash == user[0]:
                print(f"Connexion réussie. Bienvenue {username} !")
                return username, user[1]

            else:
                tentatives -= 1
                print(f"Mot de passe incorrect. Tentatives restantes : {tentatives}")

        print("Compte bloqué.")
        exit()

    finally:
        cursor.close()
        conn.close()