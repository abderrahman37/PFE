from presidio_analyzer import AnalyzerEngine
import hashlib
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.predefined_recognizers import CreditCardRecognizer, EmailRecognizer, PhoneRecognizer
from presidio_analyzer import Pattern, PatternRecognizer
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer import PatternRecognizer
from presidio_analyzer import RecognizerResult

# Initialisation de l'analyseur Presidio
analyzer = AnalyzerEngine()
class CINRecognizer(PatternRecognizer):
    def __init__(self):
        self.entity = "CIN"
        patterns = [
            Pattern(name="Morocco CIN", regex=r"\b[A-Z]{2}\d{5}\b", score=0.8),   # Ex: AB12345
            Pattern(name="France CIN", regex=r"\b\d{12}\b", score=0.8),          # Ex: 123456789012
        ]
        
        super().__init__(supported_entity=self.entity, patterns=patterns)
analyzer.registry.add_recognizer(CINRecognizer())

class DateTime2Recognizer(PatternRecognizer):
    def __init__(self):
        self.entity = "DATE_TIME2"

        # Définition des formats précis pour la détection des dates et heures
        patterns = [
            Pattern(name="ISO Format", regex=r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b", score=0.9),  # YYYY-MM-DD HH:MM:SS
            Pattern(name="US Format", regex=r"\b\d{2}/\d{2}/\d{4} \d{2}:\d{2} (AM|PM)\b", score=0.85),  # MM/DD/YYYY HH:MM AM/PM
            Pattern(name="EU Format", regex=r"\b\d{2}-\d{2}-\d{4} \d{2}:\d{2}\b", score=0.85),
            Pattern(name="Day/Month/Year", regex=r"\b\d{2}/\d{2}/\d{4}\b", score=0.85),
            Pattern(name="Year/Month/Day", regex=r"\b\d{4}/\d{2}/\d{2}\b", score=0.85),
            Pattern(name="Day-Month-Year (DD-MM-YYYY)", regex=r"\b\d{2}-\d{2}-\d{4}\b", score=0.85),  # 15-04-2002
            Pattern(name="Year-Month-Day (YYYY-MM-DD)", regex=r"\b\d{4}-\d{2}-\d{2}\b", score=0.85)
        ]
        
        super().__init__(supported_entity=self.entity, patterns=patterns)

# Ajouter le nouveau recognizer à l'analyzer
analyzer.registry.add_recognizer(DateTime2Recognizer())

def detect_pii_columns(df):
    """ Détecte les colonnes contenant des PII dans un DataFrame """
    pii_columns = []
    for col in df.columns:
        sample_values = df[col].astype(str).dropna().sample(min(5, len(df)))
        for value in sample_values:
            results = analyzer.analyze(text=value, entities=["EMAIL_ADDRESS", "PHONE_NUMBER",  "PERSON", "LOCATION", "DATE_TIME2", "NRP" ], language="en")
            if results:
                pii_columns.append(col)
                break
    return pii_columns

def anonymize_pii(df, pii_columns):
    """ Anonymise les colonnes PII d'un DataFrame """
    for col in pii_columns:
        df[col] = df[col].astype(str).apply(lambda x: hashlib.sha256(x.encode()).hexdigest()[:10])
    return df

