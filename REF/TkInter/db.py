import sqlite3
import uuid

DB_NAME = "colors.db"  # Nom de ta base existante

def generate_custom_uuid():
    """Retourne un UUID au format personnalisé 8-4-4-12"""
    raw = uuid.uuid4().hex  # 32 caractères sans tirets
    return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:]}"  # 8-4-4-12

def insert_value_with_uuid(value: int) -> str:
    if value not in [2, 3, 6, 7, 10]:
        raise ValueError("Valeur non autorisée")

    uid = generate_custom_uuid()

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO colors (uuid, value) VALUES (?, ?)", (uid, value))
    
    return uid
