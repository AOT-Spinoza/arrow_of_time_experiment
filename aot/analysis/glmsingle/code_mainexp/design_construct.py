import numpy as np
import nibabel as nib
import os
import sys
import pandas as pd
import yaml
from pathlib import Path
from glmsingle.glmsingle import GLM_single
import aot

base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
stimuli_temp_path = base_dir / "experiment/stimuli_settings_temp.yml"
core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader)
stimuli_settings_temp = yaml.load(open(stimuli_temp_path), Loader=yaml.FullLoader)  
settings_root_path = base_dir / core_settings["paths"]["settings_path"] 
video_db_path = base_dir / 'data/videos/database_originals.tsv'
video_db = pd.read_csv(video_db_path, sep='\t')

def movie_conditions_dict():
    movies = []
    for i in range(1,len(video_db)):
        if video_db['grade'][i] != 'k' and video_db['grade'][i] != 'l':   #video_db['grade'][i] == 'j' or video_db['grade'][i] == 'NA':
            movies.append(video_db['video_name'][i])
    print("videos number: ", len(movies))
    print(movies)
    movies_conditions = {}
    condnum = 0
    movies_conditions["blank"] = condnum
    for i in range(len(movies)):
        if movies[i] not in movies_conditions and movies[i] != 'blank':
            condnum += 1
            movies_conditions[movies[i]] = condnum
    print(movies_conditions)
    return movies_conditions

def construct_design_from_exp_design_yml(ymlfile, movies_conditions):
    #read in the experiment design yaml file
    settings_sample = yaml.load(open(ymlfile), Loader=yaml.FullLoader)
    #get the movie files
    movies  = settings_sample['stimuli']['movie_files']
    original_condition_list = [movies_conditions[movie] for movie in movies]
    #add blank condition to each element in the list
    original_condition_list = [[x,x]+[0,0] for x in original_condition_list]
    #flatten the list
    original_condition_list = [item for sublist in original_condition_list for item in sublist]
    print(original_condition_list)



if __name__ == '__main__':
    movie_conditions = movie_conditions_dict()
    sample_yml = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/data/experiment/settings/main/experiment_settings_sub_01_ses_01_run_01.yml'
    construct_design_from_exp_design_yml(sample_yml, movie_conditions)