from uuid import uuid4
from database.models import (
	get_robot,
	get_last_mission,
	get_all_robots,
	get_all_missions,
	get_latest_telemetry,
	save_robot
)

def is_valid_robot(robot_id):
	return get_robot(robot_id) is not None

def get_instructions(robot_id):
    from database.models import set_mission_en_cours
    set_mission_en_cours(robot_id)
    mission = get_last_mission(str(robot_id))
    return {
        "blocks": mission["blocs"]
    }

def save_telemetry(data):
	from database.models import save_telemetry as _save
	return _save(data)

def save_summary(data):
    from database.models import set_mission_effectuée
    set_mission_effectuée(data["robot_id"])
    from database.models import save_summary as _save
    return _save(data)

def save_mission(data):
	from database.models import save_mission as _save
	return _save(data)

def list_robots():
    raw = get_all_robots()
    return {"robots": [{"id": r[0], "name": r[1]} for r in raw]}

def fetch_telemetry(robot_id, limit=10):
	return get_latest_telemetry(robot_id, limit)

def fetch_all_missions(robot_id):
	return get_all_missions(robot_id)

def register_robot(robot_id: str, name: str):
	return save_robot(robot_id, name)

def estimer_blocs_deposes(telemetries):
	bloc_en_main = False
	nb_blocs_deposes = 0

	for t in reversed(telemetries):
		dist = t["distance_ultrasons"]
		ligne = t["ligne"]

		if not bloc_en_main and dist is not None and dist < 90:
			bloc_en_main = True

		elif bloc_en_main and dist is not None and dist > 100 and ligne in (4, 5, 8, 9):
			nb_blocs_deposes += 1
			bloc_en_main = False

	return nb_blocs_deposes