import operator
from typing import Dict, List, Tuple

from .methods import MethodResultType
from .types import InputDataPerGroup, ProjectsGroup
from .parameters import ParametersGroup
from .utils import fold_dict, map_dict


def greedy(data: Dict[str, InputDataPerGroup], _parameters: ParametersGroup) -> Tuple[List[int], MethodResultType]:
    return fold_dict(operator.add, [], map_dict(greedy_for_group, data)), None

def greedy_for_group(data: InputDataPerGroup) -> List[int]:
    group = data.group
    budget = data.budget
    votes_per_project = {p.id: 0 for p in group.projects}

    for profile in group.profiles:
        for vote in profile.votes:
            votes_per_project[vote] += 1

    projects = {p.id: p for p in group.projects}
    selected_projects = []
    remaining_projects = set(filter(lambda p: projects[p].cost <= budget, projects.keys()))
    while len(remaining_projects) > 0:
        best_project = max(remaining_projects, key=lambda p: votes_per_project[projects[p].id])
        budget -= projects[best_project].cost
        selected_projects.append(projects[best_project].id)
        remaining_projects.remove(best_project)
        remaining_projects = set(filter(lambda p: projects[p].cost <= budget, remaining_projects))

    return selected_projects

def split_budget(budget: int, data: Dict[str, ProjectsGroup]) -> Dict[str, int]:
    projects_costs = map_dict(lambda group: sum(p.cost for p in group.projects), data)
    total_cost = fold_dict(lambda x, g: x + g, 0, projects_costs)
    
    return map_dict(lambda c: int(budget * (c / total_cost)), projects_costs)
