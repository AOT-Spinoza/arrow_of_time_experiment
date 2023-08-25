import csv
import os
from pathlib import Path
import aot

events_tsvfile_sample = '/Users/shufanzhang/Documents/PhD/Arrow_of_time/arrow_of_time/aot/data/experiment/outputs/main/sub-01_ses-01_run-01_task-movie_events.tsv'
#events_tsvfile_sample = '/home/wang/Projects/arrow_of_time/aot/data/experiment/outputs/main/sub-01_ses-01_run-01_task-movie_events.tsv'


def count_duration_for_each_trail(events_tsvfile_sample):
    with open(events_tsvfile_sample, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        data = list(reader)
        for row in data:
            print(row)

    trail_start_dict = {}
    trail_start_dict[0] = data[0]['onset']
    trail_num = 0
    for row in data:
        if int(row['trial_nr']) != trail_num:
            trail_start_dict[int(row['trial_nr'])] = row['onset']
            trail_num = int(row['trial_nr'])

    trail_duration_dict = {}
    for i in range(len(trail_start_dict)-1):
        trail_duration_dict[i] = float(
            trail_start_dict[i+1]) - float(trail_start_dict[i])

    return trail_duration_dict


time_dict = count_duration_for_each_trail(events_tsvfile_sample)
for key in time_dict:
    print(key, time_dict[key])
