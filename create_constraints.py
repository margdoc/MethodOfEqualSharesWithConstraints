from typing import Dict
import os
import json

if len(os.sys.argv) != 4:
    print("Usage: python create_constraints.py <lower_bound_budget_usage> <upper_bound_budget_usage> <data_path>")
    exit(1)
lower_bound_budget_usage = float(os.sys.argv[1])
upper_bound_budget_usage = float(os.sys.argv[2])
data_path = os.sys.argv[3]

def load_file(path: str) -> Dict[str, str]:
    with open(path, 'r', encoding="utf-8") as f:
        meta: Dict[str, str] = {}
        assert f.readline() == 'META\n'
        line = f.readline()
        line = f.readline()
        while line != 'PROJECTS\n':
            key, value = line[:-1].split(';')
            meta[key] = value
            line = f.readline()
    return meta

constraints = {}
for filename in os.listdir(data_path):
    if filename.endswith('.pb'):
        meta = load_file(os.path.join(data_path, filename))
        budget = int(int(meta['budget']))
        unit = meta['subunit'] if 'subunit' in meta else 'citywide'
        constraints[unit] = {
            "lower_bound": int(budget * lower_bound_budget_usage),
            "upper_bound": int(budget * upper_bound_budget_usage)
        }

json.dump(constraints, open(f"{data_path}/constraints.json", "w", encoding="utf-8"), indent=4)
