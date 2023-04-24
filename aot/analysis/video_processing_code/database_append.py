import csv
import os
import aot
import yaml
from pathlib import Path

base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader)
database_path = base_dir / "data/videos/database_originals.tsv"


def read_database():
    database = []
    with open(database_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            database.append(row)
    # remove the path but keep the file name

    return database  # first row is the header


def append_new_column(key_value_dict, header, database):
    print(key_value_dict)
    database = read_database()
    # add a new column
    database[0].append(header)
    # add the values
    for i in range(1, len(database)):
        key = database[i][0]
        # print(key)
        try:
            value = key_value_dict[str(key)]
        except KeyError:
            print(f"Key {key} not found in the dictionary")
            value = "NA"
        database[i].append(value)
    return database


def write_database(database):
    with open(database_path, 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(database)
