import argparse
import json
import os
from typing import Any, Dict
from tabulate import tabulate

from src.types import ConstraintType, ConstraintsType

from .results import save_results
from .load_data import load_data
from .logger import logger
from .parameters import get_default_parameters
from .metrics import metrics_unary_desc, metrics_binary_desc
from .methods import methods_desc
from .run import RunOptions, run


def print_methods() -> None:
    print("Available methods:")
    table = [
        [name, desc] for name, desc in methods_desc.items()
    ]
    print(tabulate(table, headers=["Name", "Description"]))

def print_metrics() -> None:
    print("Available metrics:")
    table = [
        *([name, desc, False] for name, desc in metrics_unary_desc.items()),
        *([name, desc, True] for name, desc in metrics_binary_desc.items())
    ]
    print(tabulate(table, headers=["Name", "Description", "Compares results of two methods?"]))

def execute_run(data_path: str, result_path: str, run_options: RunOptions) -> None:
    data = load_data(data_path)

    if run_options.constraints.constraints is not None:
        for group, constraint in run_options.constraints.constraints.items():
            if group not in data:
                raise KeyError(f"Group {group} is not in data")
            data[group].constraint = constraint

    results = run(data, run_options)

    save_results(results, result_path)

def cli_prepare() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="sub-command help"
    )
    
    run_parser = subparsers.add_parser(
        "run",
        help="run methods and compare them with metrics",
    )
    subparsers.add_parser(
        "methods",
        help="list available methods",
    )
    subparsers.add_parser(
        "metrics",
        help="list available metrics",
    )

    run_parser.add_argument(
        '-m',
        '--method',
        type=str,
        dest='methods',
        choices=[*methods_desc.keys()] + ["all"],
        action='append',
        help='method to run (`all` to run all methods)',
    )
    run_parser.add_argument(
        '-mc',
        '--metric',
        type=str,
        dest='metrics',
        choices=[*metrics_unary_desc.keys(), *metrics_binary_desc.keys()] + ["all"],
        action='append',
        help='metric to run on methods outcomes (`all` to run all metrics)',
    )
    run_parser.add_argument(
        '-d',
        '--data',
        type=str,
        dest='data_path',
        required=True,
        help='path to data',
    )
    run_parser.add_argument(
        '-r',
        '--results',
        type=str,
        dest='results_path',
        required=True,
        help='path to a directory where results will be saved in folder in format: "YYYY-MM-DD HH:MM:SS"',
    )
    run_parser.add_argument(
        '-p',
        '--parameter',
        type=str,
        dest='parameters',
        action='append',
        help='parameter to set (format key=value)',
    )
    run_parser.add_argument(
        '--parameters_file',
        type=str,
        dest='parameters_file',
        help='path to a file with parameters (in json format)',
    )

    return parser

def cli_execute(args: argparse.Namespace) -> None:
    if args.command == "run":
        # Remove duplicates
        methods = set(args.methods or [])
        metrics = set(args.metrics or [])

        if len(methods) == 0:
            raise ValueError("No methods selected")
        if len(methods) == 1:
            binary_metrics = metrics_binary_desc.keys()
            for metric in metrics:
                if metric in binary_metrics:
                    raise ValueError("Only one method selected, but used a metric that compares outcomes of two methods")

        data_path = args.data_path
        if data_path is None or data_path == "":
            raise ValueError("No data path provided")
        if not os.path.isdir(data_path):
            raise IsADirectoryError("Data path is not a directory")
        results_path = args.results_path
        if results_path is None:
            raise ValueError("No results path provided")
        if not os.path.isdir(results_path):
            raise IsADirectoryError("Results path is not a directory")

        provided_parameters = {}
        for p in (args.parameters or []):
            splitted = p.split("=")
            if len(splitted) != 2:
                raise ValueError(f"Invalid parameter format: {p}")
            key, value = splitted
            provided_parameters[key] = value
        
        parameters_from_file: Dict[str, Dict[str, Any]] = {}
        if args.parameters_file is not None:
            if not os.path.isfile(args.parameters_file):
                raise FileNotFoundError(f"Parameters file does not exist: {args.parameters_file}")
            with open(args.parameters_file, "r", encoding="utf-8") as f:
                parameters_from_file = json.load(f)

        parameters = get_default_parameters()
        parameters.merge_with_parameters_from_cli(provided_parameters)
        parameters.merge_with_parameters(parameters_from_file)

        constraints = None
        constraints_path = os.path.join(data_path, "constraints.json")
        if os.path.isfile(constraints_path):
            with open(constraints_path, "r", encoding="utf-8") as f:
                constraints = json.load(f)
                constraints = ConstraintsType(constraints={
                    group: ConstraintType(**constraint) for group, constraint in constraints.items()
                })
 
        logger.info("Methods to run: %s", ', '.join(methods))
        if len(metrics) > 0:
            logger.info("Metrics to run: %s", ', '.join(metrics))

        if "all" in methods:
            methods = set(methods_desc.keys())
        if "all" in metrics:
            if len(methods) == 1:
                metrics = set(metrics_unary_desc.keys())
            else:
                metrics = set(metrics_unary_desc.keys()) | set(metrics_binary_desc.keys())

        logger.debug("With parameters: %s", parameters)

        run_options = RunOptions(
            methods_to_run=methods,
            metrics_to_run=metrics,
            parameters=parameters,
            constraints=constraints
        )
        execute_run(data_path, results_path, run_options)
    elif args.command == "methods":
        print_methods()
    elif args.command == "metrics":
        print_metrics()
