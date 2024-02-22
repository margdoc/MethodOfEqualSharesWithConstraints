from copy import deepcopy
import operator
from typing import Dict, List
from pabutools.election import Instance, Project as PabulibProject, ApprovalProfile, \
                               ApprovalBallot
from pabutools.rules import method_of_equal_shares
import logging
import math

from .mes import MySatisfactionMeasure
from .types import ConstraintType, InputDataPerGroup, Profile, Project
from .parameters import ParametersGroup, register_parameter
from .utils import can_afford, fold_dict, get_budgets, get_constraints, get_groups, \
                   get_projects_from_list, map_dict, merge_project_groups, zip_dict
from .logger import logger
    
class Discounts:
    def __init__(self, groups: List[str], initial_price_increase: float, discount_per_iteration: float, step: float):
        self.discounts = { group: -initial_price_increase for group in groups }
        self.discount_per_iteration = discount_per_iteration
        self.step = step

    def get_discounts(self) -> Dict[str, float]:
        return map_dict(math.tanh, self.discounts)
    
    def next_iteration(self, costs: Dict[str, int], constraints: Dict[str, int]) -> None:
        for group, (cost, constraint) in zip_dict(costs, constraints).items():
            self.discounts[group] += self.discount_per_iteration * self.step

            if constraint is None or cost >= constraint:
                continue

            self.discounts[group] += self.step * (1 - cost / constraint)


register_parameter("constrained_mes", "step", float, 0.5)
register_parameter("constrained_mes", "discount_per_iteration", float, 0.01)
register_parameter("constrained_mes", "initial_price_increase", float, 0.75)
def constrained_mes(data: Dict[str, InputDataPerGroup], parameters: ParametersGroup) -> List[int]:
    groups, budgets, constraints = get_groups(data), get_budgets(data), get_constraints(data)
    budget = fold_dict(operator.add, 0, budgets)
    all_projects: List[Project] = fold_dict(lambda x, g: x + g.projects, [], groups)
    projects_groups = { }
    for group_name, group in groups.items():
        for project in group.projects:
            projects_groups[project.id] = group_name

    projects_dict = { p.id: p for p in all_projects }
    profiles = merge_project_groups(groups).profiles

    def discounted(p: Project, discount: float) -> Project:
        new_p = deepcopy(p)
        new_p.cost = int(p.cost * max(0.000001, 1 - discount))
        return new_p

    def get_costs_per_group(chosen_ids: List[int]) -> Dict[str, int]:
        costs = map_dict(lambda _: 0, groups)
        for _id in chosen_ids:
            costs[projects_groups[_id]] += projects_dict[_id].cost
        return costs

    def get_discount(cost: int, constraint: ConstraintType) -> float:
        if constraint is None or cost >= constraint:
            return 0
        return 1 - cost / constraint

    def add_discounts(discounts1: Dict[str, float], discounts2: Dict[str, float]) -> Dict[str, float]:
        return map_dict(lambda g: min(1, g[0] + g[1]), zip_dict(discounts1, discounts2))

    def get_discounts(costs: Dict[str, int]) -> Dict[str, float]:
        return map_dict(lambda g: get_discount(g[0], g[1]), zip_dict(costs, constraints))

    logger.debug("Budget: %i" % budget)
    discounts = Discounts(groups.keys(), parameters["initial_price_increase"], parameters["discount_per_iteration"], parameters["step"])
    previously_chosen: List[int] = []
    iteration = 0
    while True:
        iteration += 1

        discounts_dict = discounts.get_discounts()
        projects: List[Project] = fold_dict(lambda x, g: x + list(map(lambda p: discounted(p, g[1]), g[0].projects)),
                                            [],
                                            zip_dict(groups, discounts_dict))

        chosen_ids = constrained_mes_one_step(budget, projects, profiles)
        chosen_projects = get_projects_from_list(projects_dict, chosen_ids)

        costs = get_costs_per_group(chosen_ids)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Iteration %i" % iteration)
            # logger.debug("Chosen projects: %s" % chosen_ids)
            logger.debug("Overall cost: %i" % sum(costs.values()))
            logger.debug("Costs: %s" % costs)
            logger.debug("Discounts: %s" % discounts_dict)

        if not can_afford(budget, chosen_projects):
            logger.debug("Chosen projects exceed the budget")
            return previously_chosen
        if chosen_ids == previously_chosen:
            logger.debug("No changes in the chosen projects")
            return chosen_ids

        discounts.next_iteration(costs, constraints)
        previously_chosen = chosen_ids

def constrained_mes_one_step(budget: int, projects: List[Project], profiles: List[Profile]) -> List[int]:
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