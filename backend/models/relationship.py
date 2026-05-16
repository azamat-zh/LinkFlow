from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class RelationshipType(str, Enum):
    mentor_company = "mentor_company"
    partner_initiative = "partner_initiative"
    company_programme = "company_programme"


class RelationshipState(str, Enum):
    pending = "pending"
    active = "active"
    stale = "stale"
    completed = "completed"
    closed = "closed"


class SessionLog(BaseModel):
    date: datetime
    notes: str
    logged_by: str


class Relationship(BaseModel):
    id: str
    relationship_type: RelationshipType
    actor_a_id: str
    actor_b_id: str
    state: RelationshipState
    match_score: float
    match_reasoning: str
    session_log: list[SessionLog]
    created_at: datetime
    last_updated: datetime
    programme_id: str


class RelationshipCreate(BaseModel):
    relationship_type: RelationshipType
    actor_a_id: str
    actor_b_id: str
    match_score: float
    match_reasoning: str
    programme_id: str
