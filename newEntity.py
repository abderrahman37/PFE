from presidio_analyzer import Pattern, PatternRecognizer, AnalyzerEngine, RecognizerRegistry
from presidio_anonymizer import AnonymizerEngine
import sys
from presidio_anonymizer.entities import OperatorConfig
sys.stdout.reconfigure(encoding='utf-8')


# ==============================
# 📌 Définition du CINRecognizer
# ==============================

class CINRecognizer(PatternRecognizer):
    def __init__(self):
        # Nom de l'entité
        self.entity = "CIN"
        
        # Définition des patterns de CIN pour différents pays
        patterns = [
            Pattern(name="Morocco CIN", regex=r"\b[A-Z]{2}\d{5}\b", score=0.8),   # Ex: AB12345
            Pattern(name="France CIN", regex=r"\b\d{12}\b", score=0.8),          # Ex: 123456789012
        ]
        
        # Initialisation du recognizer avec les patterns
        super().__init__(supported_entity=self.entity, patterns=patterns)

# ============================
# 📌 Initialisation de Presidio
# ============================

# Création de l'instance du reconnaisseur
cin_recognizer = CINRecognizer()

# Création de l'engine de reconnaissance
analyzer = AnalyzerEngine()

# Enregistrement du nouveau reconnaisseur
recognizer_registry = RecognizerRegistry()
recognizer_registry.add_recognizer(cin_recognizer)
analyzer.registry = recognizer_registry

# ============================
# 📌 Test de la détection du CIN
# ============================

text = "Mon CIN marocain est AB12345 et mon CIN français est 123456789012."

# Analyse du texte
results = analyzer.analyze(text=text, entities=["CIN"], language="en")

# Affichage des résultats
print("\n📌 Résultats de la détection :")
for result in results:
    print(f"🔍 Entité détectée: {result.entity_type}, Début: {result.start}, Fin: {result.end}, Score: {result.score}")

# ==============================
# 📌 Anonymisation du CIN détecté
# ==============================

# Création de l'engine d'anonymisation
anonymizer = AnonymizerEngine()

# Anonymisation des CIN détectés
anonymized_text = anonymizer.anonymize(
    text, 
    results, 
    operators={"CIN": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 5, "from_end": False})}
)

print("\n📌 Texte anonymisé :")
print(anonymized_text.text)
