from typing import Dict
import os
import json

if len(os.sys.argv) != 3:
    print("Usage: python create_constraints.py <budget usage> <path to data>")
    exit(1)
budget_usage = float(os.sys.argv[1])
data_path = os.sys.argv[2]

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
        if 'subunit' in meta:
            constraints[meta['subunit']] = int(int(meta['budget']) * budget_usage)
        else:
            constraints['citywide'] = int(int(meta['budget']) * budget_usage)

json.dump(constraints, open(f"{data_path}/constraints.json", "w", encoding="utf-8"), indent=4)
