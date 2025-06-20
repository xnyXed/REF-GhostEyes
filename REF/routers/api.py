from fastapi import APIRouter, Request, Query
from uuid import UUID
from services.logic import (
    get_instructions,
    save_telemetry,
    save_summary,
	save_mission,
    is_valid_robot,
	register_robot,
	fetch_telemetry,
	fetch_all_missions,
	list_robots,
)
from database.models import save_simulation
from schemas import TelemetryData, SummaryData, MissionData, SimulationData

router = APIRouter()

@router.get("/instructions")
async def instructions(robot_id: str):
	if not is_valid_robot(robot_id):
		return {"error": "Robot not registered"}
	return get_instructions(robot_id)

@router.post("/telemetry")
async def telemetry(request: Request):
    payload = await request.json()
    validated = TelemetryData(**payload)
    save_telemetry(validated.dict())
    return {}

@router.post("/summary")
async def summary(request: Request):
    payload = await request.json()
    validated = SummaryData(**payload)
    save_summary(validated.dict())
    return {}

@router.post("/mission")
async def mission(request: Request):
    payload = await request.json()
    validated = MissionData(**payload)
    save_mission(validated.dict())
    return {}

@router.get("/missions")
async def missions(robot_id: UUID):
	if not is_valid_robot(robot_id):
		return {"error": "Robot not registered"}
	return fetch_all_missions(str(robot_id))

@router.post("/simulation")
async def simulation(request: Request):
	payload = await request.json()
	validated = SimulationData(**payload)
	save_simulation(validated.dict())
	return {}

@router.post("/register")
async def register():
	robot_id = register_robot()
	return {"robot_id": robot_id}

@router.get("/telemetry")
async def telemetry(robot_id: UUID, limit: int = Query(10, ge=1, le=100)):
	if not is_valid_robot(robot_id):
		return {"error": "Robot not registered"}
	return fetch_telemetry(str(robot_id), limit)

@router.get("/api/robots")
def get_robots():
	return list_robots()