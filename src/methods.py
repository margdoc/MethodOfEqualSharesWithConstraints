import operator
from typing import Callable, Dict, List, Tuple

from .types import InputDataPerGroup, MethodResultType
from .parameters import ParametersGroup
from .utils import can_afford, fold_dict, get_all_projects_dict, get_projects_from_list, \
                   get_budgets, get_groups
from .mes import modified_mes, mes
from .greedy import greedy
from .constrained_mes import constrained_mes

MethodType = Callable[[Dict[str, InputDataPerGroup], ParametersGroup], Tuple[List[int], MethodResultType]]

def method_decorator(func: MethodType) -> MethodType:
    def wrapper(data: Dict[str, InputDataPerGroup], options: ParametersGroup) -> List[int]:
        result = func(data, options)
        groups, budgets = get_groups(data), get_budgets(data)
        total_budget = fold_dict(operator.add, 0, budgets)
        assert can_afford(total_budget,
                          get_projects_from_list(get_all_projects_dict(groups), result[0]))
        return result
    return wrapper

methods_desc: Dict[str, str] = {
    "greedy": "Greedy algorithm",
    "mes_add_one": "Method of Equal Shares (AddOne)",
    # "modified_mes": "Modified Method of Equal Shares", # TODO: add description
    "constrained_mes": "Constrained Method of Equal Shares", # TODO: add description
}
methods: Dict[str, MethodType] = {
    "greedy": method_decorator(greedy),
    "mes_add_one": method_decorator(mes),
    # "modified_mes": method_decorator(modified_mes),
    "constrained_mes": method_decorator(constrained_mes),
}
assert set(methods.keys()) == set(methods_desc.keys())

def get_methods() -> Dict[str, MethodType]:
    return methods
