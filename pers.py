import pandas as pd
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from sqlalchemy import Engine, Inspector

# 🎯 Configuration de l'Analyzer avec les entités de type PERSON, LOCATION, EMAIL
analyzer = AnalyzerEngine()

# Ajouter un recognizer pour les numéros de téléphone (tu l'as déjà fait)
phone_recognizer = PatternRecognizer(
    supported_entity="PHONE_NUMBER",
    patterns=phone_patterns,
    context=["téléphone", "phone", "mobile", "contact", "tel", "appeler"]
)
analyzer.registry.add_recognizer(phone_recognizer)

# Ajouter un recognizer pour les emails
email_recognizer = PatternRecognizer(
    supported_entity="EMAIL_ADDRESS",
    patterns=[Pattern(name="email", regex=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", score=0.8)],
    context=["email", "courriel"]
)
analyzer.registry.add_recognizer(email_recognizer)

# Ajouter un recognizer pour les personnes (PERSON)
person_recognizer = PatternRecognizer(
    supported_entity="PERSON",
    patterns=[Pattern(name="person_name", regex=r"[A-Z][a-z]+ [A-Z][a-z]+", score=0.9)],  # simple nom prénom
    context=["name", "prenom", "nom", "full name"]
)
analyzer.registry.add_recognizer(person_recognizer)

# Ajouter un recognizer pour les adresses (LOCATION)
location_recognizer = PatternRecognizer(
    supported_entity="LOCATION",
    patterns=[Pattern(name="location", regex=r"\b(?:[A-Za-z]+(?: [A-Za-z]+){1,3})\b", score=0.85)],  # simple adresse
    context=["adresse", "location", "ville", "pays"]
)
analyzer.registry.add_recognizer(location_recognizer)

# 🔄 Scanner toutes les tables
for table_name in Inspector.get_table_names():
    print(f"\nAnalyse de la table : {table_name}")
    
    # 📥 Charger les données (limite 1000 lignes pour éviter les performances trop lourdes)
    query = f"SELECT * FROM {table_name} LIMIT 1000"
    df = pd.read_sql(query, Engine)
    
    # 🔍 Parcourir les colonnes et détecter les PII
    for column in df.columns:
        column_lower = column.lower()
        pii_found = False
        
        print(f"    Analyse de la colonne : {column}")
        
        # Vérification des colonnes qui pourraient contenir des PII
        for value in df[column].dropna().astype(str):
            # Ignorer les valeurs vides ou trop courtes
            if pd.isna(value) or len(value.strip()) <= 1:
                continue
            
            # Vérification des entités PII
            try:
                results = analyzer.analyze(
                    text=value,
                    entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "LOCATION", "DATE_TIME"],
                    score_threshold=0.8,  # Augmenter le seuil pour une meilleure précision
                    language="fr"
                )
                
                if results:
                    pii_detected = [(res.entity_type, res.score) for res in results]
                    print(f"      PII détectée dans {column} : {value} | {pii_detected}")
                    pii_found = True

            except ValueError as e:
                # Gestion de l'erreur "No matching recognizers were found"
                if "No matching recognizers were found" in str(e):
                    # Si aucune détection d'entité, essayer avec d'autres regex personnalisées
                    pass
                else:
                    print(f"      Erreur lors de l'analyse de {value}: {e}")
        
        if pii_found:
            print(f"    La colonne {column} contient des PII.")
