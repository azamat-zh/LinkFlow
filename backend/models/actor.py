from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ActorType(str, Enum):
    company = "company"
    mentor = "mentor"
    partner = "partner"
    service_provider = "service_provider"


class ActorProfile(BaseModel):
    id: str
    name: str
    actor_type: ActorType
    sector: str
    stage: str
    tags: list[str]
    needs: list[str]
    expertise: list[str]
    location: str
    bio: str
    source_file: str
    created_at: datetime
    programme_history: list[str]


class ActorCreate(BaseModel):
    name: str
    actor_type: ActorType
    sector: str
    stage: str
    tags: list[str]
    needs: list[str]
    expertise: list[str]
    location: str
    bio: str
    source_file: str
    programme_history: list[str]
