from copy import deepcopy
from typing import Callable, List, Dict, Tuple, TypeVar

from .types import ConstraintType, Profile, Project, ProjectsGroup, InputDataPerGroup


T = TypeVar('T')
T2 = TypeVar('T2')

def map_dict(f: Callable[[T], T2], data: Dict[str, T]) -> Dict[str, T2]:
    return { k: f(v) for k, v in data.items() }

def map_dict_with_key(f: Callable[[str, T], T2], data: Dict[str, T]) -> Dict[str, T2]:
    return { k: f(k, v) for k, v in data.items() }

def fold_dict(f: Callable[[T2, T], T2], initial_value: T2, data: Dict[str, T]) -> T2:
    t = initial_value
    for v in data.values():
        t = f(t, v)
    return t

def zip_dict(data1: Dict[str, T], data2: Dict[str, T2]) -> Dict[str, tuple[T, T2]]:
    return { k: (v, data2[k]) for k, v in data1.items() }

def unzip_dict(data: Dict[str, tuple[T, T2]]) -> Tuple[Dict[str, T], Dict[str, T2]]:
    return { k: v[0] for k, v in data.items() }, { k: v[1] for k, v in data.items() }

def get_profiles(data: Dict[str, ProjectsGroup]) -> List[Profile]:
    return fold_dict(lambda x, g: x + g.profiles, [], data)

def get_projects(data: Dict[str, ProjectsGroup]) -> List[Project]:
    return fold_dict(lambda x, g: x + g.projects, [], data)

def merge_project_groups(data: Dict[str, ProjectsGroup]) -> ProjectsGroup:
    profiles: Dict[int, Profile] = {}
    
    listed_profiles: List[Profile] = get_profiles(data)
    for profile in listed_profiles:
        if profile.id in profiles:
            profiles[profile.id].votes += profile.votes
        else:
            profiles[profile.id] = deepcopy(profile)

    return ProjectsGroup(
        projects=get_projects(data),
        profiles=list(profiles.values())
    )

def get_all_projects_dict(data: Dict[str, ProjectsGroup]) -> Dict[int, Project]:
    projects: List[Project] = fold_dict(lambda x, g: x + g.projects, [], data)
    return { p.id: p for p in projects }

def get_projects_from_list(projects_dict: dict[int, Project], projects: List[int]) -> List[Project]:
    return [projects_dict[p] for p in projects]

def can_afford(budget: int, projects: List[Project]) -> bool:
    return sum(p.cost for p in projects) <= budget

def merge_input_data(data: Dict[str, InputDataPerGroup]) -> InputDataPerGroup:
    return InputDataPerGroup(
        group=merge_project_groups(map_dict(lambda d: d.group, data)),
        budget=sum(d.budget for d in data.values()),
        constraint=None, # TODO
    )

def get_groups(data: Dict[str, InputDataPerGroup]) -> Dict[str, ProjectsGroup]:
    return map_dict(lambda d: d.group, data)

def get_budgets(data: Dict[str, InputDataPerGroup]) -> Dict[str, int]:
    return map_dict(lambda d: d.budget, data)

def get_constraints(data: Dict[str, InputDataPerGroup]) -> Dict[str, ConstraintType]:
    return map_dict(lambda d: d.constraint, data)
