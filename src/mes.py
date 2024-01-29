from copy import deepcopy
import operator
from typing import Dict, List, Collection
from pabutools.election import Instance, Project as PabulibProject, ApprovalProfile, \
                               ApprovalBallot, SatisfactionMeasure, AbstractBallot,  \
                               AbstractProfile
from pabutools.rules import method_of_equal_shares
from pabutools.utils import Numeric

from .types import InputDataPerGroup, Profile, Project
from .parameters import ParametersGroup, register_parameter
from .utils import can_afford, fold_dict, get_budgets, get_groups, get_projects_from_list, \
                   map_dict, merge_project_groups, zip_dict


class MySatisfactionMeasure(SatisfactionMeasure):
    def __init__(
        self,
        instance: Instance,
        profile: AbstractProfile,
        ballot: AbstractBallot,
    ) -> None:
        SatisfactionMeasure.__init__(self, instance, profile, ballot)

    def _get_project_sat(self, project: Project) -> Numeric:
        return int(project in self.ballot) * project.cost

    def sat(self, projects: Collection[Project]) -> Numeric:
        return sum(self._get_project_sat(p) for p in projects)

    def sat_project(self, project: Project) -> Numeric:
        return self._get_project_sat(project)

register_parameter("modified_mes", "step", float, 0.1)
register_parameter("modified_mes", "part_of_initial_budget", float, 0.8)
def modified_mes(data: Dict[str, InputDataPerGroup], parameters: ParametersGroup) -> List[int]:
    groups, budgets = get_groups(data), get_budgets(data)
    budget = int(fold_dict(operator.add, 0, budgets) * parameters["part_of_initial_budget"])
    all_projects: List[Project] = fold_dict(lambda x, g: x + g.projects, [], groups)

    discount_steps = map_dict(lambda b: b * parameters["step"] / budget, budgets)
    discount_steps['citywide'] = 0 # TODO: ?

    projects_dict = { p.id: p for p in all_projects }
    profiles = merge_project_groups(groups).profiles

    def discounted(p: Project, discount: float, iteration: int) -> Project:
        new_p = deepcopy(p)
        new_p.cost = int(p.cost * (1 - discount * iteration))
        return new_p

    previously_chosen: List[int] = []
    iteration = 0
    while True:
        iteration += 1

        projects: List[Project] = fold_dict(lambda x, g: x + list(map(lambda p: discounted(p, g[1], iteration), g[0].projects)),
                                            [],
                                            zip_dict(groups, discount_steps))

        chosen_ids = modified_mes_one_step(budget, projects, profiles)
        chosen_projects = get_projects_from_list(projects_dict, chosen_ids)

        if not can_afford(budget, chosen_projects):
            return previously_chosen
        previously_chosen = chosen_ids

def modified_mes_one_step(budget: int, projects: List[Project], profiles: List[Profile]) -> List[int]:
    projects_dict = { p.id: PabulibProject(str(p.id), p.cost) for p in projects }
    instance = Instance(projects_dict.values(), budget)
    profile = ApprovalProfile([
            ApprovalBallot([projects_dict[v] for v in p.votes])
            for p in profiles
        ]) #.as_multiprofile() # TODO: check if this helps

    outcome = method_of_equal_shares(
        instance,
        profile,
        sat_class=MySatisfactionMeasure,
    )

    return [int(p.name) for p in outcome]

register_parameter("mes_add_one", "step", int, 20)
def mes(data: Dict[str, InputDataPerGroup], parameters: ParametersGroup) -> List[int]:
    groups, budgets = get_groups(data), get_budgets(data)
    budget = fold_dict(operator.add, 0, budgets)
    projects: List[Project] = fold_dict(lambda x, g: x + g.projects, [], groups)
    profiles = merge_project_groups(groups).profiles

    return mes_folded(budget, projects, profiles, parameters)

def mes_folded(budget: int, projects: List[Project], profiles: List[Profile], parameters: ParametersGroup) -> List[int]:
    projects_dict = { p.id: PabulibProject(str(p.id), p.cost) for p in projects }
    instance = Instance(projects_dict.values(), budget)
    profile = ApprovalProfile([
            ApprovalBallot([projects_dict[v] for v in p.votes])
            for p in profiles
        ]) #.as_multiprofile() # TODO: check if this helps

    outcome = method_of_equal_shares(
        instance,
        profile,
        sat_class=MySatisfactionMeasure,
        voter_budget_increment=parameters["step"],
    )

    return [int(p.name) for p in outcome]
