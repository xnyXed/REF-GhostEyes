from typing import List
from pydantic import BaseModel

class TelemetryData(BaseModel):
    robot_id: str
    vitesse: float
    distance_ultrasons: float
    statut_deplacement: str
    ligne: int
    statut_pince: bool

class SummaryData(BaseModel):
    robot_id: str

class MissionData(BaseModel):
    robot_id: str
    blocs: List[int]

class SimulationData(BaseModel):
	robot_id: str
	distance_total: float
	nb_blocs_prevus: int
	vitesse_cible: float