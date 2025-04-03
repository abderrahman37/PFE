from sqlalchemy import create_engine, inspect
import pandas as pd
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.predefined_recognizers import CreditCardRecognizer, EmailRecognizer, PhoneRecognizer
from tabulate import tabulate
from presidio_analyzer import Pattern, PatternRecognizer  # Ajout pour le CINRecognizer

# 🔹 Définition du CINRecognizer
class CINRecognizer(PatternRecognizer):
    def __init__(self):
        self.entity = "CIN"
        patterns = [
            Pattern(name="Morocco CIN", regex=r"\b[A-Z]{2}\d{5}\b", score=0.8),   # Ex: AB12345
            Pattern(name="France CIN", regex=r"\b\d{12}\b", score=0.8),          # Ex: 123456789012
        ]
        super().__init__(supported_entity=self.entity, patterns=patterns)

# 🔹 Configuration de la connexion à la base de données
DB_TYPE = "postgresql"  # Adapter selon le SGBD (ex: "mssql+pyodbc", "mysql")
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "attijaridb"
DB_USER = "postgres"
DB_PASSWORD = "123456"

# Création de l'engine SQLAlchemy
engine = create_engine(f"{DB_TYPE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# 🔹 Initialisation de Presidio
analyzer = AnalyzerEngine() 
analyzer.registry.add_recognizer(CINRecognizer())  # ✅ Ajout du CINRecognizer

# 🔹 Fonction pour scanner une table et détecter les PII
def detect_pii_from_table(table_name):
    query = f"SELECT * FROM {table_name} LIMIT 50;"  # Limite à 50 lignes pour éviter surcharge
    df = pd.read_sql(query, engine)
    
    pii_columns = set()  # Utilisation d'un set pour éviter les doublons
    
    for column in df.columns:
        for value in df[column].dropna():
            value = str(value)  # Convertir en string si nécessaire
            results = analyzer.analyze(
                text=value, 
                entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "PERSON", "LOCATION", "DATE_TIME", "CIN" , "NRP" ],  # ✅ Ajout de "CIN"
                language="en"
            )
            if results:
                pii_columns.add(column)  # Ajouter la colonne contenant des PII

    return pii_columns

# 🔹 Scanner toutes les tables de la base
inspector = inspect(engine)
tables = inspector.get_table_names()
all_pii_columns = []

for table in tables:
    pii_columns = detect_pii_from_table(table)
    if pii_columns:
        all_pii_columns.append((table, list(pii_columns)))

# 🔹 Afficher les résultats
if all_pii_columns:
    print(tabulate(all_pii_columns, headers=["Table", "Colonnes PII"], tablefmt="grid"))
else:
    print("✅ Aucune donnée PII détectée.")
