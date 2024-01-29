import os
from typing import Dict, List, Tuple

from .types import InputDataPerGroup, Profile, Project, ProjectsGroup


def load_file(path: str) -> Tuple[Dict[str, str], ProjectsGroup]:
    with open(path, 'r') as f:
        meta: Dict[str, str] = {}
        assert f.readline() == 'META\n'
        line = f.readline()
        line = f.readline()
        while line != 'PROJECTS\n':
            key, value = line[:-1].split(';')
            meta[key] = value
            line = f.readline()
        projects = []
        line = f.readline()
        line = f.readline()
        while line != 'VOTES\n':
            _id, cost, _, _, _, _, _, _, _ = line[:-1].split(';')
            # longitude=float(longitude) if longitude else None
            # latitude=float(latitude) if latitude else None
            projects.append(Project(_id=int(_id), cost=int(cost)))
            line = f.readline()
        profiles = []
        line = f.readline()
        line = f.readline()
        while line:
            # _id, age, sex, voting_method, votes_str, district = line[:-1].split(';')
            values = line[:-1].split(';')
            votes: List[int] = [int(vote) for vote in values[4].split(',')] if values[4] != "" else []
            # age = int(values[1]) if values[1] else None
            district = values[5] if len(values) == 6 else None
            profiles.append(Profile(_id=int(values[0]), votes=votes, district=district))
            line = f.readline()
    return meta, ProjectsGroup(projects=projects, profiles=profiles)

def load_data(path: str) -> Dict[str, InputDataPerGroup]:
    districts: Dict[str, InputDataPerGroup] = {}
    citywide: InputDataPerGroup | None = None

    for filename in os.listdir(path):
        if filename.endswith('.pb'):
            meta, projects_group = load_file(os.path.join(path, filename))
            if 'subunit' in meta:
                districts[meta['subunit']] = InputDataPerGroup(group=projects_group, budget=int(meta['budget']), constraint=None)
            else:
                if citywide is not None:
                    raise Exception('Multiple citywide files found')
                citywide = InputDataPerGroup(group=projects_group, budget=int(meta['budget']), constraint=None)

    if citywide is None:
        raise Exception('No citywide file found')
    return districts | { 'citywide': citywide }