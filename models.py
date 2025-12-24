from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Tuple, List, Literal
import uuid
import time

class VisibilityLevel(Enum):
    UNKNOWN = 0
    SUSPECTED = 1
    IDENTIFIED = 2
    DETAILED = 3

class Unit(BaseModel):
    id: str
    faction_id: str
    position: Tuple[int, int]
    symbol: str
    visibility: Dict[str, VisibilityLevel]  # viewer_id -> level

class Faction(BaseModel):
    id: str
    name: str
    color: str

class Tile(BaseModel):
    position: Tuple[int, int]
    visibility_modifier: int

class MapState(BaseModel):
    width: int
    height: int
    tiles: Dict[Tuple[int, int], Tile]

class Player(BaseModel):
    id: str
    name: str | None = None
    faction_id: str | None = None

class Session(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    narrator_id: str | None = None

    state: Literal['Open', 'Locked', 'Running', 'Ended'] = 'Open'

    players: Dict[str, Player] = Field(default_factory=dict)
    events: List['Event'] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)

    def add_player(self, player_id: str, name: str | None = None):
        if self.state != "Open":
            raise ValueError("Session is not open")

        if player_id in self.players:
            return  # idempotent join
        self.players[player_id] = Player(id=player_id, name=name)
        self.log("player_joined", {"player_id": player_id})

    def remove_player(self, player_id: str):
        if player_id in self.players:
            del self.players[player_id]
            self.log("player_left", {"player_id": player_id})
    
    def lock(self):
        if self.state != "Open":
            return
        self.state = "Locked"
        self.log("session_locked", {})

    def unlock(self):
        if self.state != "Locked":
            raise ValueError("Only locked sessions can be unlocked")
        self.state = "Open"
        self.log("session_unlocked", {})
        
    def log(self, event_type: str, payload: dict):
        event = Event(
            ts=time.time(),
            type=event_type,
            payload=payload
        )
        self.events.append(event)

class Event(BaseModel):
    ts: float
    type: str
    payload: dict
