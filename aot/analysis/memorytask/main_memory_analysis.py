import os
import pandas as pd
import copy
import random
import yaml
from pathlib import Path
import matplotlib.pyplot as plt
from copy import deepcopy
import csv
import aot

base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
stimuli_temp_path = base_dir / "experiment/stimuli_settings_temp.yml"
core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader)
stimuli_settings_temp = yaml.load(open(stimuli_temp_path), Loader=yaml.FullLoader)

settings_root_path = base_dir / core_settings["paths"]["settings_path"]
main_settings_dir = base_dir / core_settings["paths"]["settings_path"] / "main"
memory_settings_dir = base_dir / core_settings["paths"]["settings_path"] / "memory_main"
memory_settings_answers_dir = memory_settings_dir / "answers"
memory_task_output_dir = base_dir / core_settings["paths"]["output_path"] / "memory_main"

subject_number = core_settings["various"]["subject_number"]
run_number = core_settings["various"]["run_number"]
session_number = core_settings["various"]["session_number"]
unique_video_number_per_session = core_settings["various"][
    "unique_video_number_per_session"
]
img_number_per_session = unique_video_number_per_session

def read_memory_output(file):
    output_list = []
    memory_output = pd.read_csv(file)
    for index, row in memory_output.iterrows():
        output_list.append(tuple(row))
    print(output_list)
    return output_list

def read_memory_answer(file):
    answer_list = []
    memory_answer = pd.read_csv(file, sep='\t', header=None)
    for index, row in memory_answer.iterrows():
        answer_list.append(tuple(row))
    print(answer_list)
    return answer_list


def memory_task_accuracy(sub,ses):
    #zeropad sub and ses
    sub = str(sub).zfill(2)
    ses = str(ses).zfill(2)
    memory_output_file = str(memory_task_output_dir / f"sub-{sub}_ses-{ses}_run-01_task-memory_memory.csv")
    memory_answer_file = str(memory_settings_answers_dir / f"answer_dict_sub_{sub}_ses_{ses}.tsv")
    memory_output = read_memory_output(memory_output_file)
    memory_answer = read_memory_answer(memory_answer_file)
    print(len(memory_output))
    print(len(memory_answer))
    correct = 0
    for i in range(len(memory_output)):
        if memory_output[i][1] == "j" and memory_answer[i][1] == "Y":
            correct += 1
        elif memory_output[i][1] == "k" and memory_answer[i][1] == "N":
            correct += 1
    print(f"sub {sub} ses {ses} accuracy: ",correct/len(memory_output))
    return correct/len(memory_output)

    





memory_task_accuracy(1,1)
memory_task_accuracy(1,2)