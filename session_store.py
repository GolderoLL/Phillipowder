import uuid
from models import Session, MapState

sessions: dict[str, Session] = {}

def create_session_internal(narrator_id: str | None = None) -> Session:
    session_id = str(uuid.uuid4())[:8]

    session = Session(
        id=session_id,
        narrator_id=narrator_id or "narrator",
        factions={},
        units={},
        map=MapState(width=10, height=10, tiles={})
    )

    sessions[session.id] = session
    return session  

def delete_session(session_id: str):
    return sessions.pop(session_id, None)

def list_sessions():
    return list(sessions.values())

def get_session(session_id: str):
    return sessions.get(session_id)
