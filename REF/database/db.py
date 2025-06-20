import sqlite3

DB_PATH = "robots.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_cursor():
    conn = get_connection()
    return conn, conn.cursor()

def commit_and_close(conn):
    conn.commit()
    conn.close()