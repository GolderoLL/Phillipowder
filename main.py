from typing import List, Dict
from dataclasses import dataclass, field
import uuid
import time
from models import Session, Unit, MapState
from state import SESSIONS
from visibility import get_visible_unit
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from session_store import create_session_internal, delete_session, list_sessions, get_session, sessions

app = FastAPI()

@app.get("/")
def root():
    return RedirectResponse("/narrator")

@app.post("/session/{session_id}")
def api_create_session(session_id: str, narrator_id: str):
    SESSIONS[session_id] = Session(
        id=session_id,
        narrator_id=narrator_id,
        factions={},
        units={},
        map=MapState(width=10, height=10, tiles={})
    )
    return {"status": "created"}

@app.post("/session/{session_id}/unit")
def add_unit(session_id: str, unit: Unit):
    SESSIONS[session_id].units[unit.id] = unit
    return {"status": "unit added"}

@app.get("/session/{session_id}/view/{viewer_id}")
def view_session(session_id: str, viewer_id: str):
    session = SESSIONS[session_id]
    visible_units = []

    for unit in session.units.values():
        vu = get_visible_unit(unit, viewer_id)
        if vu:
            visible_units.append(vu)

    return {"units": visible_units}

@app.post("/narrator/create")
def narrator_create():
    session = create_session_internal()
    return RedirectResponse(
        url=f"/narrator/{session.id}",
        status_code=303
    )

@app.post("/narrator/{session_id}/delete")
def narrator_delete(session_id: str):
    sessions.pop(session_id, None)
    return RedirectResponse("/narrator", status_code=303)

@app.get("/narrator/sessions")
def narrator_list_sessions():
    return [
        {
            "id": s.id,
            "locked": s.locked,
            "players": len(s.players)
        }
        for s in list_sessions()
    ]

@app.post("/narrator/{session_id}/lock")
def narrator_lock(session_id: str):
    s = get_session(session_id)
    s.lock()
    return RedirectResponse(
        url=f"/narrator",
        status_code=303
    )

@app.post("/join/{session_id}")
def join_session(session_id: str, player_id: str):
    s = get_session(session_id)
    s.add_player(player_id)
    return {"status": "joined"}

@app.post("/narrator/{session_id}/unlock")
def narrator_unlock(session_id: str):
    s = get_session(session_id)
    s.unlock()
    return RedirectResponse(
        url=f"/narrator",
        status_code=303
    )

@app.get("/narrator/{session_id}", response_class=HTMLResponse)
def narrator_dashboard(session_id: str):
    try:
        s = get_session(session_id)
    except KeyError:
        raise HTTPException(404)

    action_button = ""
    if s.state == "Open" or s.state == "Running":
        action_button = f"""
        <form method="post" action="/narrator/{s.id}/lock">
            <button>Lock Scenario</button>
        </form>
        """
    elif s.state == "Locked":
        action_button = f"""
        <form method="post" action="/narrator/{s.id}/unlock">
            <button>Unlock Scenario</button>
        </form>
        """
    action_button += f"""
        <form method="post" action="/narrator/{s.id}/delete">
            <button>Delete Session</button>
        </form>
        """
    return f"""
    <h1>Session {s.id}</h1>
    <p>State: {s.state}</p>
    <p>Players: {len(s.players)}</p>

    {action_button}
    """

@app.get("/narrator", response_class=HTMLResponse)
def narrator_root():
    session_list = ""

    for s in sessions.values():
        session_list += f"""
        <li>
            <a href="/narrator/{s.id}">Session {s.id}</a>
            (state: {s.state})
            <form method="post" action="/narrator/{s.id}/delete" style="display:inline;">
                <button>Delete</button>
            </form>
        </li>
        """

    return f"""
    <h1>Narrator Panel</h1>

    <form method="post" action="/narrator/create">
        <button>Create New Session</button>
    </form>

    <h2>Existing Sessions</h2>
    <ul>
        {session_list or "<li>No sessions yet</li>"}
    </ul>
    """

@dataclass 
class Session: 
    id: str
    created_at: float
    locked: bool = False

    players: List[str] = field(default_factory=list)
    factions: Dict[str, dict] = field(default_factory=dict)

    @staticmethod
    def create():
        return Session(
            id=str(uuid.uuid4())[:8],
            created_at=time.time()
        )