import sqlalchemy
import pandas as pd
from sqlalchemy import text  # Importation de 'text' pour la gestion des requêtes

# Connexion à la base de données PostgreSQL
DATABASE_URL = "postgresql://postgres:123456@localhost:5432/postgres"
engine = sqlalchemy.create_engine(DATABASE_URL)

def get_table_names():
    """ Récupère la liste des tables dans la base de données """
    query = text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            return [row[0] for row in result]  # Accès via l'indice du tuple
    except Exception as e:
        print(f"Erreur lors de la récupération des noms de tables : {e}")
        return []

def get_table_data(table_name):
    """ Récupère les données d'une table donnée """
    query = text(f"SELECT * FROM {table_name}")
    try:
        return pd.read_sql(query, con=engine)
    except Exception as e:
        print(f"Erreur lors de la récupération des données de la table {table_name}: {e}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur
