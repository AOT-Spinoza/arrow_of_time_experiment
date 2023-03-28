import csv
import os
import aot
import yaml
from pathlib import Path
import aot.analysis.video_processing_code.database_append as db_append

base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
stimuli_temp_path = base_dir / "experiment/stimuli_settings_temp.yml"
core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader)
grades_path = base_dir / core_settings["paths"]["grades_path"]


def read_all_grades():
    all_grades = []
    for file in os.listdir(grades_path):
        if file.endswith(".csv"):
            with open(grades_path / file, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    all_grades.append(row)
    # remove the path but keep the file name
    for i in range(len(all_grades)):  # remove the S_ cap from the name
        all_grades[i][0] = all_grades[i][0].split("/")[-1]
        S_name = all_grades[i][0]
        name = S_name[2:]
        all_grades[i][0] = name
    # make a dict
    all_grades = dict(all_grades)
    return all_grades


if __name__ == "__main__":
    all_grades = read_all_grades()
    # print(all_grades)
    db = db_append.read_database()
    db = db_append.append_new_column(all_grades, "grade", db)
    print(db)
    db_append.write_database(db)
