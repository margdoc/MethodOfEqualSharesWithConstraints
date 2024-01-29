# Method of Equal Shares with Constraints

## Requirements
- Python 3
- pip
- packages from `requirements.txt` (to install run `pip install -r requirements.txt`)

## Example usage
```bash
python main.py run -m all -mc all -d ../data/Warszawa\ 2023/ -r results
```

## Usage
To see all available options run:
```bash
python main.py run --help
```
To see all available methods run:
```bash
python main.py methods
```
To see all available metrics run:
```bash
python main.py metrics
```
To change logs level use `LOG_LEVEL` environment variable. For example:
```bash
LOG_LEVEL=debug python main.py run -m all -mc all -d ../data/Warszawa\ 2023/ -r results
```

`run` command creates subdirectory in `results` directory with name in format `YYYY-MM-DD HH:MM:SS` and saves there
- `logs.txt` - logs
- `methods_outcomes.json` - projects choosen by each method
- `results.json` - score of each method for each metric (global and per district)
It also creates symlink `latest` to this directory.

## Visual results
Available visualizations:
- `lower_constraint_satisfaction_table.py`

All of them take as input `methods_outcomes.json` or/and `results.json` files from `results/latest` directory.

## Other scripts

### `create_constraints.py`
Creates `constraints.json` file in `data path`` directory with constraints for each district as a percentage of the budget.
It is lower bound constraint for each district.
#### Usage
```
python create_constraints.py [part of the budget] [data path]
```
#### Example
```
python create_constraints.py 0.5 example_data/Warszawa\ 2023/
```