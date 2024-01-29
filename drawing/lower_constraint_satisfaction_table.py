
import os
import json
import matplotlib.pyplot as plt
import pandas as pd

results_directory = "results/latest/"
results_file = os.path.join(results_directory, "results.json")
save_to = os.path.join(results_directory, "lower_constraint_satisfaction.png")

fig, ax = plt.subplots()

# hide axes
fig.patch.set_visible(False)
ax.axis('off')
ax.axis('tight')

results = json.load(open(results_file, "r", encoding="utf-8"))

algorithms = None
keys = []
values = []
for district, district_results in results["district_results"].items():
    scores = district_results["results"]["lower_constraint_satisfaction"]
    if algorithms is None:
        algorithms = list(scores.keys())
    keys.append(district)
    values.append(list(scores.values()))

assert algorithms is not None

df = pd.DataFrame(values, columns=algorithms, index=keys)

table = ax.table(cellText=df.values, colLabels=df.columns, rowLabels=df.index, loc='center')

if len(algorithms) >= 3 or (len(algorithms) == 2 and algorithms[0] != "greedy"):
    max_indexes = []
    min_indexes = []

    for i, row in enumerate(values):
        max_value = 0
        max_index = 0
        for j, cell in enumerate(row):
            if algorithms[j] == "greedy":
                continue
            value = cell
            if value > max_value:
                max_value = value
                max_index = j

        max_indexes.append(max_index)

    for i, row in enumerate(values):
        min_value = int(1e9)
        min_index = 0
        for j, cell in enumerate(row):
            if algorithms[j] == "greedy":
                continue
            value = cell
            if value < min_value:
                min_value = value
                min_index = j

        min_indexes.append(min_index)

    for i, j in enumerate(max_indexes):
        table[i + 1, j].get_text().set_color("green")
    for i, j in enumerate(min_indexes):
        table[i + 1, j].get_text().set_color("red")

fig.tight_layout()

plt.savefig(save_to)
