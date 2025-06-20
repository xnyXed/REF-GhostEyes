import json
from database.db import get_cursor, commit_and_close
from datetime import datetime

# Setup DB tables
conn, cur = get_cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS robots (
	robot_id TEXT PRIMARY KEY
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS telemetry (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	robot_id TEXT NOT NULL,
	vitesse REAL NOT NULL,
	distance_ultrasons REAL,
	statut_deplacement TEXT NOT NULL,
	ligne INTEGER NOT NULL,
	statut_pince BOOLEAN NOT NULL,
	timestamp TEXT NOT NULL
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS summary (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	robot_id TEXT,
	vitesse_moyenne REAL
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS missions (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	robot_id TEXT NOT NULL,
	blocs TEXT NOT NULL,
	timestamp TEXT NOT NULL
)''')

cur.execute('''
CREATE TABLE IF NOT EXISTS simulations (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	robot_id TEXT NOT NULL,
	timestamp TEXT NOT NULL,
	distance_total REAL,
	nb_blocs_prevus INTEGER,
	vitesse_cible REAL
)
''')

commit_and_close(conn)

def get_robot(robot_id):
	conn, cur = get_cursor()
	cur.execute("SELECT robot_id FROM robots WHERE robot_id = ?", (robot_id,))
	result = cur.fetchone()
	commit_and_close(conn)
	return result

def save_telemetry(data):
	timestamp = datetime.utcnow().isoformat()
	conn, cur = get_cursor()
	cur.execute(
		"INSERT INTO telemetry (robot_id, vitesse, distance_ultrasons, statut_deplacement, ligne, statut_pince, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
		(str(data["robot_id"]), data["vitesse"], data["distance_ultrasons"], data["statut_deplacement"], data["ligne"], int(data["statut_pince"]), timestamp)
	)
	commit_and_close(conn)

def save_summary(data):
	conn, cur = get_cursor()
	cur.execute(
		"INSERT INTO summary (robot_id, vitesse_moyenne) VALUES (?, NULL)",
		(str(data["robot_id"]),)
	)
	commit_and_close(conn)

def save_mission(data):
    conn, cur = get_cursor()
    timestamp = datetime.utcnow().isoformat()
    blocs_json = json.dumps(data["blocs"])
    cur.execute(
        "INSERT INTO missions (robot_id, blocs, timestamp, statut) VALUES (?, ?, ?, ?)",
        (str(data["robot_id"]), blocs_json, timestamp, "non_effectuée")
    )
    commit_and_close(conn)

def set_mission_en_cours(robot_id):
    conn, cur = get_cursor()
    cur.execute(
        "SELECT id FROM missions WHERE robot_id = ? AND statut = 'non_effectuée' ORDER BY timestamp ASC LIMIT 1",
        (robot_id,)
    )
    row = cur.fetchone()
    if row:
        mission_id = row[0]
        cur.execute(
            "UPDATE missions SET statut = 'en_cours' WHERE id = ?",
            (mission_id,)
        )
    commit_and_close(conn)

def set_mission_effectuée(robot_id):
    conn, cur = get_cursor()
    cur.execute(
        "SELECT id FROM missions WHERE robot_id = ? AND statut = 'en_cours' ORDER BY timestamp DESC LIMIT 1",
        (robot_id,)
    )
    row = cur.fetchone()
    if row:
        mission_id = row[0]
        cur.execute(
            "UPDATE missions SET statut = 'effectuée' WHERE id = ?",
            (mission_id,)
        )
    commit_and_close(conn)

def save_robot(robot_id, name):
	conn, cur = get_cursor()
	cur.execute("INSERT INTO robots (robot_id, name) VALUES (?, ?)", (robot_id, name))
	commit_and_close(conn)
    
def get_all_robots():
    conn, cur = get_cursor()
    cur.execute("SELECT robot_id, name FROM robots")
    result = cur.fetchall()
    commit_and_close(conn)
    return result

def get_last_mission(robot_id):
    conn, cur = get_cursor()
    cur.execute(
        """SELECT blocs, statut FROM missions WHERE robot_id = ? AND statut IN ('non_effectuée', 'en_cours') ORDER BY timestamp ASC LIMIT 1""", 
		(robot_id,)
    )
    result = cur.fetchone()
    commit_and_close(conn)

    if result:
        blocs = json.loads(result[0])
        statut = result[1]
    else:
        blocs = []
        statut = None

    return {
        "robot_id": robot_id,
        "blocs": blocs,
        "statut": statut
    }

def get_all_missions(robot_id):
    conn, cur = get_cursor()
    cur.execute(
        "SELECT blocs, timestamp FROM missions WHERE robot_id = ? ORDER BY timestamp DESC",
        (robot_id,)
    )
    rows = cur.fetchall()
    commit_and_close(conn)

    return [
        {
            "blocs": json.loads(blocs),
            "timestamp": timestamp
        } for blocs, timestamp in rows
    ]

def get_latest_telemetry(robot_id, limit=10):
	conn, cur = get_cursor()
	cur.execute("""
		SELECT vitesse, distance_ultrasons, statut_deplacement, ligne, statut_pince
		FROM telemetry
		WHERE robot_id = ?
		ORDER BY id DESC
		LIMIT ?
	""", (str(robot_id), limit))
	rows = cur.fetchall()
	commit_and_close(conn)

	return [
		{
			"vitesse": row[0],
			"distance_ultrasons": row[1],
			"statut_deplacement": row[2],
			"ligne": row[3],
			"statut_pince": bool(row[4])
		}
		for row in rows
	]

def save_simulation(data):
	timestamp = datetime.utcnow().isoformat()
	conn, cur = get_cursor()
	cur.execute(
		'''INSERT INTO simulations (robot_id, timestamp, distance_total, nb_blocs_prevus, vitesse_cible)
		VALUES (?, ?, ?, ?, ?)''',
		(str(data["robot_id"]), timestamp, data["distance_total"], data["nb_blocs_prevus"], data["vitesse_cible"])
	)
	commit_and_close(conn)

def get_last_simulation(robot_id):
	conn, cur = get_cursor()
	cur.execute(
		'''SELECT timestamp, distance_total, nb_blocs_prevus, vitesse_cible
		FROM simulations
		WHERE robot_id = ?
		ORDER BY timestamp DESC
		LIMIT 1''',
		(str(robot_id),)
	)
	row = cur.fetchone()
	commit_and_close(conn)
	if not row:
		return None
	return {
		"timestamp": row[0],
		"distance": row[1],
		"nb_blocs": row[2],
		"vitesse": row[3]
	}