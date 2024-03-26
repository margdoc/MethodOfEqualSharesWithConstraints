from typing import Dict, List, Optional, Tuple
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

class ConstraintType(BaseModel):
    lower_bound: Optional[int]
    upper_bound: Optional[int]

    @classmethod
    def none(self):
        return ConstraintType(lower_bound=None, upper_bound=None)

class ConstraintsType(BaseModel):
    constraints: Optional[Dict[str, ConstraintType]]

class InputDataPerGroup(BaseModel):
    group: ProjectsGroup
    budget: int
    constraint: ConstraintType
