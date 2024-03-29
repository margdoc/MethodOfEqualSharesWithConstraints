from typing import Callable, Dict, List, Tuple

from .types import InputDataPerGroup
from .utils import merge_input_data


MetricResultType = float | int

MetricScores = Dict[str, MetricResultType]
MetricsScores = Dict[str, MetricScores]

def metric_for_merged_data(metric):
    def wrapper(data: Dict[str, InputDataPerGroup], *args) -> MetricResultType:
        return metric(merge_input_data(data), *args)
    return wrapper

def metric_from_only_for_group(metric):
    return (metric_for_merged_data(metric), metric)

def average_satisfaction(data: InputDataPerGroup, selected_projects: List[int]) -> float:
    selected_projects_set = set(selected_projects)
    total_satisfaction = 0
    for profile in data.group.profiles:
        votes = set(profile.votes)
        total_satisfaction += len(votes & selected_projects_set)
    return total_satisfaction / len(data.group.profiles)

def better_than(data: InputDataPerGroup, selected_projects: List[int], worse_projects: List[int]) -> float:
    selected_projects_set = set(selected_projects)
    worse_projects_set = set(worse_projects)
    prefers_selected = 0
    for profile in data.group.profiles:
        votes = set(profile.votes)
        from_selected = len(votes & selected_projects_set)
        from_worse = len(votes & worse_projects_set)
        if from_selected > from_worse:
            prefers_selected += 1
    return prefers_selected / len(data.group.profiles)

def cost(data: InputDataPerGroup, selected_projects: List[int]) -> int:
    selected_projects_set = set(selected_projects)
    return sum(p.cost for p in data.group.projects if p.id in selected_projects_set)

def budget_usage(data: InputDataPerGroup, selected_projects: List[int]) -> float:
    return cost(data, selected_projects) / data.budget

def number_of_selected_projects(data: InputDataPerGroup, selected_projects: List[int]) -> int:
    selected_projects_set = set(selected_projects)
    return len(list(s for s in data.group.projects if s.id in selected_projects_set))

def lower_constraint_satisfaction(data: InputDataPerGroup, selected_projects: List[int]) -> float:
    if data.constraint is None:
        return 0
    return cost(data, selected_projects) / data.constraint

MetricUnaryForGroupType = Callable[[InputDataPerGroup, List[int]], MetricResultType]
MetricUnaryType = Callable[[Dict[str, InputDataPerGroup], List[int]], MetricResultType]
MetricBinaryForGroupType = Callable[[InputDataPerGroup, List[int], List[int]], MetricResultType]
MetricBinaryType = Callable[[Dict[str, InputDataPerGroup], List[int], List[int]], MetricResultType]

metrics_unary_desc: Dict[str, str] = {
    "average_satisfaction": "Average satisfaction (number of selected projects that are also in the profile)",
    "cost": "Total cost of selected projects",
    "budget_usage": "Total cost of selected projects divided by budget",
    "number_of_selected_projects": "Number of selected projects",
    "lower_constraint_satisfaction": "Total cost of selected projects divided by constraint",
}
metrics_unary: Dict[str, Tuple[MetricUnaryType | None, MetricUnaryForGroupType | None]] = {
    "average_satisfaction": metric_from_only_for_group(average_satisfaction),
    "cost": metric_from_only_for_group(cost),
    "budget_usage": metric_from_only_for_group(budget_usage),
    "number_of_selected_projects": metric_from_only_for_group(number_of_selected_projects),
    "lower_constraint_satisfaction": (None, lower_constraint_satisfaction),
}
metrics_binary_desc: Dict[str, str] = {
    "better_than": "Percentage of profiles that prefer projects selected by the first method over projects selected by the second method",
}
metrics_binary: Dict[str, Tuple[MetricBinaryType | None, MetricBinaryForGroupType | None]] = {
    "better_than": metric_from_only_for_group(better_than),
}

assert set(metrics_unary.keys()) == set(metrics_unary_desc.keys())
assert set(metrics_binary.keys()) == set(metrics_binary_desc.keys())
