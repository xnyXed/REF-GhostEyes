from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from dateutil import parser  # ajout important

from routers import api
from services.logic import (
    list_robots,
    fetch_all_missions,
    fetch_telemetry,
    register_robot,
    estimer_blocs_deposes,
    get_last_simulation
)

app = FastAPI(debug=True)
app.include_router(api.router)

# Static files (CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates (HTML)
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def ihm(request: Request, selected_id: str = None, display_mode: str = "chiffre"):
    robots = list_robots()["robots"]
    robot_id = selected_id if selected_id and any(r["id"] == selected_id for r in robots) else (robots[0]["id"] if robots else None)

    missions = fetch_all_missions(robot_id) if robot_id else []
    telemetries = fetch_telemetry(robot_id, limit=1000) if robot_id else []

    for m in missions:
        raw_ts = m.get("timestamp")
        try:
            dt = parser.isoparse(raw_ts)
            m["timestamp"] = dt.strftime("%d/%m/%Y - %H:%M:%S")
        except Exception:
            pass

    class MissionView:
        def __init__(self, blocs, timestamp, statut):
            self.blocs = blocs
            self.timestamp = timestamp
            self.statut = statut

    missions = [
        MissionView(m["blocs"], m["timestamp"], m.get("statut", ""))
        for m in missions
    ]

    vitesse_moyenne = round(sum(t["vitesse"] for t in telemetries) / len(telemetries), 2) if telemetries else 0
    nb_blocs_deposes = estimer_blocs_deposes(telemetries)

    sim = get_last_simulation(robot_id) if robot_id else None
    simulateur = sim if sim else {"distance": "—", "nb_blocs": "—", "vitesse": "—", "timestamp": "—"}

    comparaison = {
        "delta_temps": 2.4,
    }

    bloc_colors = {
        2: "🟡",
        3: "🔴",
        6: "🌸",
        7: "🟣",
        10: "🟢",
    }

    return templates.TemplateResponse(
        "ihm_dashboard.html",
        {
            "request": request,
            "robot_id": robot_id,
            "robots": robots,
            "missions": missions,
            "telemetry": {
                "vitesse_moyenne": vitesse_moyenne,
                "nb_blocs_deposes": nb_blocs_deposes,
                "entries": telemetries,
            },
            "simulateur": simulateur,
            "comparaison": comparaison,
            "display_mode": display_mode,
            "bloc_colors": bloc_colors,
        },
    )


@app.post("/register")
async def register_robot_ihm(robot_id: str = Form(...), name: str = Form(...)):
    register_robot(robot_id, name)
    return RedirectResponse(url="/", status_code=303)