import pandas as pd
import re
from sqlalchemy import create_engine
import sys

# 🔹 Correction encodage Windows
sys.stdout.reconfigure(encoding="utf-8")

# 🔹 Modifier ces paramètres avec tes informations
DB_TYPE = "postgresql"  # "postgresql" pour PostgreSQL, "mssql" pour SQL Server
USER = "postgres"
PASSWORD = "123456"
HOST = "localhost"  # "localhost" ou l'adresse du serveur
DATABASE = "attijaridb"

# ✅ Connexion avec SQLAlchemy
if DB_TYPE == "postgresql":
    engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}/{DATABASE}")
elif DB_TYPE == "mssql":
    engine = create_engine(f"mssql+pyodbc://{USER}:{PASSWORD}@{HOST}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server")
else:
    raise ValueError("Type de base de données non supporté !")

# 🔹 Nom de la table à analyser
TABLE_NAME = "clients"

# 📥 Charger les données depuis la base
query = f"SELECT * FROM {TABLE_NAME} LIMIT 1000"
df = pd.read_sql(query, engine)

# 🔎 Définition des Regex pour détecter les PII
regex_patterns = { 
    "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "Téléphone": r"^\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}$",
    "Adresse IP": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "Nom/Prénom": r"\b[A-ZÀ-Ÿ][a-zà-ÿ]+(?:[-'\s][A-ZÀ-Ÿa-zà-ÿ]+)*\b",  # Détection basique des prénoms et noms
    "Adresse": r"\d{1,5}\s[\w\s\-]+(?:rue|avenue|boulevard|place|impasse|chemin|route|allée|cours|street|road|lane|drive|boulevard|sq|terrace|court|way|driveway|st|blvd)[,\s][\w\s\-]+(?:[A-Za-z]{2,}){1,2}"
}


# 📅 Vérifier si une colonne contient des dates (ex: Date de naissance)
def is_date(column_data):
    try:
        parsed_dates = pd.to_datetime(column_data, format="%Y-%m-%d", errors="coerce")
        if parsed_dates.notna().sum() > len(column_data) * 0.5:  # Si plus de 50% sont des dates
            return "Date de naissance"
    except:
        pass
    return "Inconnu"

# 🔍 Fonction de détection des PII
def detect_pii(column_data):
    for pii_type, pattern in regex_patterns.items():
        if column_data.astype(str).str.match(pattern, na=False).any():
            return pii_type
    return "Inconnu"

# 🚀 Scanner toutes les colonnes et détecter les PII
pii_results = {col: is_date(df[col]) if is_date(df[col]) != "Inconnu" else detect_pii(df[col]) for col in df.columns}

# 📊 Afficher le rapport des colonnes contenant des PII
print("🔍 Résumé des PII détectés :")
for col, pii_type in pii_results.items():
    if pii_type != "Inconnu":
        print(f"-> {col} : {pii_type}")

# 🔚 Fermer la connexion
engine.dispose()
