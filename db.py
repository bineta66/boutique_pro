import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="hellome13",
            database="boutique_pro"
        )
        cursor = conn.cursor()
        return conn, cursor
    except Error as err:
        print("Erreur de connexion :", err)
        return None, None