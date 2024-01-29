"""
Parameters are used to pass variable values to the code. They are grouped by group
and each parameter has its name and a type.
Parameters are provided in the following format: `[group].[parameter]=[value]`

For example: `mes.voter_budget_increment=10`
It can be provided by:
- passing `--parameters [group].[parameter]=[value]` to the CLI
- providing a `--parameters_file [file]` to the CLI, where `[file]` is a JSON file
"""

from copy import deepcopy
from typing import Any, Dict, Type

class Parameter:
    """
    Single parameter with a value and a type.
    Value should be of the given type.
    """
    value: Any
    type: Type

    def __init__(self, value: Any, t: Type):
        self.value = value
        self.type = t

    def __repr__(self) -> str:
        return f"{self.value}"

class ParametersGroup:
    """
    Group of parameters. Used to keep track of the parameters and its types.
    """
    _parameters: Dict[str, Parameter]

    def __init__(self):
        self._parameters = {}

    def __getitem__(self, name: str) -> Any:
        return self._parameters[name].value

    def __setitem__(self, name: str, value: Any) -> None:
        if name not in self._parameters:
            raise ValueError(f"Unknown parameter: {name}")
        self._parameters[name].value = self._parameters[name].type(value)

    def get_type(self, name: str) -> Type:
        return self._parameters[name].type

    def register_parameter(self, name: str, parameter: Parameter) -> None:
        self._parameters[name] = parameter

    def __contains__(self, name: str) -> bool:
        return name in self._parameters

    def __repr__(self) -> str:
        return repr(self._parameters)

class Parameters:
    _parameters: Dict[str, ParametersGroup]

    def __init__(self):
        self._parameters = {}

    def register_parameter(self, group: str, name: str, t: Type, default_value: Any) -> None:
        if not isinstance(default_value, t):
            raise ValueError(f"Default value for parameter {group}.{name} is not of the correct type: {t}")

        if group not in self._parameters:
            self._parameters[group] = ParametersGroup()
        self._parameters[group].register_parameter(name, Parameter(value=default_value, t=t))

    def merge_with_parameters_from_cli(self, provided_parameters: Dict[str, Any]) -> None:
        groups: Dict[str, Dict[str, Any]] = { parameter.split(".")[0]: {} for parameter in provided_parameters.keys() }
        for parameter, value in provided_parameters.items():
            group, name = parameter.split(".")
            groups[group][name] = value

        self.merge_with_parameters(groups)

    def merge_with_parameters(self, provided_parameters: Dict[str, Dict[str, Any]]) -> None:
        for group, parameters in provided_parameters.items():
            if group not in self._parameters:
                raise ValueError(f"Unknown parameter group: {group}")
            for name, value in parameters.items():
                if name not in self._parameters[group]:
                    raise ValueError(f"Unknown parameter: {group}.{name}")
                self._parameters[group][name] = self._parameters[group].get_type(name)(value)

    def __getitem__(self, group: str) -> ParametersGroup:
        return self._parameters[group]

    def __contains__(self, group: str) -> bool:
        return group in self._parameters

    def __repr__(self) -> str:
        return repr(self._parameters)

default_parameters: Parameters = Parameters()

def register_parameter(group: str, name: str, t: Type, default_value) -> None:
    default_parameters.register_parameter(group, name, t, default_value)

def get_default_parameters() -> Parameters:
    return deepcopy(default_parameters)
    