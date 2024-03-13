import os
from typing import Dict, List, Tuple

from .types import ConstraintType, InputDataPerGroup, Profile, Project, ProjectsGroup


def load_file(path: str) -> Tuple[Dict[str, str], ProjectsGroup]:
    with open(path, 'r') as f:
        # META
        meta: Dict[str, str] = {}
        assert f.readline() == 'META\n'
        line = f.readline()
        while line != 'PROJECTS\n':
            key, value = line[:-1].split(';')
            meta[key] = value
            line = f.readline()

        # PROJECTS
        projects = []
        line = f.readline()
        keys = line[:-1].split(';')
        id_index = keys.index('project_id')
        cost_index = keys.index('cost')
        line = f.readline()
        while line != 'VOTES\n':
            splitted = line[:-1].split(';')
            _id = splitted[id_index]
            cost = splitted[cost_index]
            projects.append(Project(_id=int(_id), cost=int(cost)))
            line = f.readline()

        # VOTES
        profiles = []
        line = f.readline()
        keys = line[:-1].split(';')
        voter_id_index = keys.index('voter_id')
        votes_index = keys.index('vote')
        neighborhood_index = keys.index('neighborhood') if 'neighborhood' in keys else None
        line = f.readline()
        while line:
            splitted = line[:-1].split(';')
            _id = splitted[voter_id_index]
            votes = [int(v) for v in splitted[votes_index].split(',')] if splitted[votes_index] != '' else []
            district = splitted[neighborhood_index] if neighborhood_index is not None else None
            profiles.append(Profile(_id=int(_id), votes=votes, district=district))
            line = f.readline()
    return meta, ProjectsGroup(projects=projects, profiles=profiles)

def load_data(path: str) -> Dict[str, InputDataPerGroup]:
    districts: Dict[str, InputDataPerGroup] = {}
    citywide: InputDataPerGroup | None = None

    for filename in os.listdir(path):
        if filename.endswith('.pb'):
            meta, projects_group = load_file(os.path.join(path, filename))
            if 'subunit' in meta:
                districts[meta['subunit']] = InputDataPerGroup(group=projects_group, budget=int(meta['budget']), constraint=ConstraintType.none())
            else:
                if citywide is not None:
                    raise Exception('Multiple citywide files found')
                citywide = InputDataPerGroup(group=projects_group, budget=int(meta['budget']), constraint=ConstraintType.none())

    if citywide is None:
        raise Exception('No citywide file found')
    return districts | { 'citywide': citywide }