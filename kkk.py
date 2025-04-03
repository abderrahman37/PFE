import psycopg2

# Connexion à la base de données PostgreSQL
conn = psycopg2.connect(
    dbname="attijaridb",
    user="postgres",
    password="123456",
    host="localhost",  # Ou l'adresse de ton serveur
    port="5432"
)
cursor = conn.cursor()

cursor.execute("SELECT * FROM transactions")
columns = [desc[0] for desc in cursor.description]
print("Colonnes détectées :", columns)

cursor.close()
conn.close()
