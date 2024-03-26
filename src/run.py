import time
from typing import Dict, Set, Tuple

from .types import ConstraintsType, DataShort, InputDataPerGroup
from .results import MethodOutcome, Results
from .logger import logger
from .parameters import Parameters, ParametersGroup
from .metrics import MetricsScores, metrics_unary, metrics_binary
from .methods import methods


class RunOptions:
    methods_to_run: Set[str]
    metrics_to_run: Set[str]
    parameters: Parameters
    constraints: ConstraintsType

    def __init__(self, methods_to_run: Set[str], metrics_to_run: Set[str], parameters: Parameters, constraints: ConstraintsType):
        self.methods_to_run = methods_to_run
        self.metrics_to_run = metrics_to_run
        self.parameters = parameters
        self.constraints = constraints

def run_methods(data: Dict[str, InputDataPerGroup], run_options: RunOptions) -> Dict[str, MethodOutcome]:
    results: Dict[str, MethodOutcome] = {}

    for name, method in methods.items():
        if name not in run_options.methods_to_run:
            continue
        logger.info("Running method %s...", name)
        start = time.time()
        parameters_group = run_options.parameters[name] if name in run_options.parameters \
                              else ParametersGroup()
        result = method(data, parameters_group)
        end = time.time()
        results[name] = MethodOutcome(
            selected_projects=result,
            time=end - start
        )
    return results

def run_metrics(data: Dict[str, InputDataPerGroup], outcomes: Dict[str, MethodOutcome], run_options: RunOptions) -> Tuple[MetricsScores, Dict[str, MetricsScores]]:
    metrics_scores: MetricsScores = {}
    metrics_scores_for_group: Dict[str, MetricsScores] = {
        group_name: {} for group_name in data.keys()
    }

    for metric_name, (metric_u, metric_u_for_group) in metrics_unary.items():
        if metric_name not in run_options.metrics_to_run:
            continue
        for method_name, outcome in outcomes.items():
            if metric_u is not None:
                if metric_name not in metrics_scores:
                    metrics_scores[metric_name] = {}
                metrics_scores[metric_name][method_name] = metric_u(data, outcome.selected_projects)
            if metric_u_for_group is not None:
                for group_name, group in data.items():
                    if metric_name not in metrics_scores_for_group[group_name]:
                        metrics_scores_for_group[group_name][metric_name] = {}
                    metrics_scores_for_group[group_name][metric_name][method_name] = metric_u_for_group(group, outcome.selected_projects)

    for metric_name, (metric_b, metric_b_for_group) in metrics_binary.items():
        if metric_name not in run_options.metrics_to_run:
            continue
        for method_name, outcome in outcomes.items():
            for method_name2, outcome2 in outcomes.items():
                if method_name == method_name2:
                    continue
                method_entry_name = f"{method_name} vs {method_name2}"
                if metric_b is not None:
                    if metric_name not in metrics_scores:
                        metrics_scores[metric_name] = {}
                    metrics_scores[metric_name][method_entry_name] = metric_b(data, outcome.selected_projects, outcome2.selected_projects)
                if metric_b_for_group is not None:
                    for group_name, group in data.items():
                        if metric_name not in metrics_scores_for_group[group_name]:
                            metrics_scores_for_group[group_name][metric_name] = {}
                        metrics_scores_for_group[group_name][metric_name][method_entry_name] = metric_b_for_group(group, outcome.selected_projects, outcome2.selected_projects)

    return metrics_scores, metrics_scores_for_group

def run(data: Dict[str, InputDataPerGroup], run_options: RunOptions) -> Results:
    outcomes = run_methods(data, run_options)
    metrics_scores, metrics_results_for_group = run_metrics(data, outcomes, run_options)
    return Results(outcomes=outcomes,
                   metrics_scores=metrics_scores,
                   district_results=metrics_results_for_group,
                   used_parameters=run_options.parameters.to_dict(),
                   constraints=run_options.constraints,
                   data_short={
                        group_name: DataShort(
                            budget=group.budget,
                            lower_bound=round(group.constraint.lower_bound / group.budget, 2),
                            upper_bound=round(group.constraint.upper_bound / group.budget, 2),
                        ) for group_name, group in data.items()
                   })
