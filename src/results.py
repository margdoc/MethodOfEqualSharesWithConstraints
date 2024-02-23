import json
from typing import Any, Dict, List
from datetime import datetime
import os
from pathlib import Path
from pydantic import BaseModel

from .metrics import MetricsScores
from .logger import get_logs

# TODO: correctly handle polish letters in files

class MethodOutcome(BaseModel):
    selected_projects: List[int]
    time: float

class Results(BaseModel):
    outcomes: Dict[str, MethodOutcome]
    metrics_scores: MetricsScores
    district_results: Dict[str, MetricsScores]
    used_parameters: Dict[str, Dict[str, Any]]

def district_results_to_json(district_results: Dict[str, MetricsScores]) -> Dict[str, Any]:
    return {
        key: {
            "results": {
                metric: scores
                for metric, scores in value.items()
            }
        }
        for key, value in district_results.items()
    }

def format_results(results: Results) -> str:
    methods_times = {}

    for name, outcome in results.outcomes.items():
        methods_times[name] = outcome.time

    json_dict = {
        "execution time (in seconds)": methods_times,
        "results": {
            metric: scores
            for metric, scores in results.metrics_scores.items()
        },
        "district_results": district_results_to_json(results.district_results)
    }

    return json.dumps(json_dict, indent=4)

def format_outcomes(outcomes: Dict[str, List[int]]) -> str:
    return json.dumps(outcomes)

def read_outcomes(outcomes: str) -> Dict[str, List[int]]:
    return json.loads(outcomes)

def save_results(results: Results, results_path: str) -> None:
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    results_dir = Path(results_path) / now_str
    results_dir.mkdir(parents=True)

    outcomes = {
        name: outcome.selected_projects
        for name, outcome in results.outcomes.items()
    }
    with open(results_dir / "methods_outcomes.json", 'w', encoding="utf-8") as file:
        file.write(format_outcomes(outcomes))

    with open(results_dir / "results.json", 'w', encoding="utf-8") as file:
        file.write(format_results(results))

    with open(results_dir / "logs.txt", 'w', encoding="utf-8") as file:
        file.write(get_logs())

    with open(results_dir / "parameters.json", 'w', encoding="utf-8") as file:
        file.write(json.dumps(results.used_parameters, indent=4))

    latest_path = Path(results_path) / "latest"
    if latest_path.is_symlink():
        latest_path.unlink()
    elif latest_path.exists():
        raise Exception("latest is not a symlink")
    latest_path.symlink_to(results_dir.absolute(), target_is_directory=True)
