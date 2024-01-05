import csv
import os
from pathlib import Path
import aot

# events_tsvfile_sample = '/Users/shufanzhang/Documents/PhD/Arrow_of_time/arrow_of_time/aot/data/experiment/outputs/main/sub-01_ses-01_run-01_task-movie_events.tsv'
# events_tsvfile_sample = '/home/wang/Projects/arrow_of_time/aot/data/experiment/outputs/main/sub-01_ses-01_run-01_task-movie_events.tsv'
events_tsvfile_sample = "/tank/shared/2022/arrow_of_time/arrow_of_time_exp/aot/data/experiment/outputs/main/sub-01_ses-01_run-04_task-movie_events.tsv"

def count_beginning_blank_time(events_tsvfile_sample):
    with open(events_tsvfile_sample, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        data = list(reader)

        first_t_onset = None
        first_movie_onset = None
        first_t = False
        for row in data:
            if row["response"] == "t":
                if first_t == False:
                    first_t_onset = row["onset"]
                    print("first t onset:",first_t_onset)
                    first_t = True
            elif row["event_type"] == "movie":
                first_movie_onset = row["onset"]
                print("first movie onset:",first_movie_onset)
                break
    return float(first_movie_onset) - float(first_t_onset)




    


# count durations between each movie event
def conunt_duration_for_each_movie(events_tsvfile_sample):
    with open(events_tsvfile_sample, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        data = list(reader)

        movie_start_list = []
        for i in range(len(data)):
            if data[i]["event_type"] == "movie":
                #print(data[i]["onset"])
                movie_start_list.append(data[i]["onset"])
        
        movie_duration_dict = {}
        for i in range(len(movie_start_list)-1):
            movie_duration_dict[i] = float(
                movie_start_list[i+1]) - float(movie_start_list[i])
            
        return movie_duration_dict

movie_duration_dict = conunt_duration_for_each_movie(events_tsvfile_sample)
for key in movie_duration_dict:
    print(key, movie_duration_dict[key])

print("begining blank time:",count_beginning_blank_time(events_tsvfile_sample))

    
