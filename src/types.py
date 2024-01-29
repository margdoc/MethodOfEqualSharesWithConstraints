from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Project(BaseModel):
    id: int = Field(..., alias='_id')
    cost: int

class Profile(BaseModel):
    id: int = Field(..., alias='_id')
    votes: List[int]
    district: Optional[str]

class ProjectsGroup(BaseModel):
    projects: List[Project]
    profiles: List[Profile]

ConstraintType = Optional[int]
ConstraintsType = Optional[Dict[str, ConstraintType]]

class InputDataPerGroup(BaseModel):
    group: ProjectsGroup
    budget: int
    constraint: ConstraintType
