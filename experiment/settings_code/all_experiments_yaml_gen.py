import sys
import os
import numpy as np
import pandas as pd
import yaml
import copy
import random
import csv
import ffmpeg
import pandas as pd

#load settings_template.yml
dispath_information= pd.read_csv('video_dispatch.tsv',delimiter='\t')
#turn the information_list_originals into a list
dispath_information = dispath_information.values.tolist()
print(dispath_information)

settings_temp = yaml.load(open('base_settings.yaml'), Loader=yaml.FullLoader)
rootpath = settings_temp['path']['rootpath']
settings_folder_path = rootpath+settings_temp['path']['settings_path']
stimuli_path = rootpath+settings_temp['path']['stimuli_path'] #the path of the stimuli on the local folder


#target_stimuli_path = settings_temp['path']['server_stimuli_path'] #the path of the stimuli on the server
target_stimuli_path = rootpath+settings_temp['path']['stimuli_path']
#print(settings_temp['stimuli']['movie_files'])
group_number = settings_temp['various']['group_number']
#create settings files for each group folder

#all_subject_folders=[folder for folder in os.listdir(stimuli_path) if folder != 'output' and folder != '.DS_Store']


#we neet to construct stimulis videos names from the original videos names: add S_ and R_S_, then dupicate the list and shuffle it
def organize_videos_by_group():
    group_dict = {}
    group_dict_grading = {}
    group_dict_labeling = {}
    for i in range(group_number):
        group_dict['group'+str(i+1)] = []
        group_dict_grading['group'+str(i+1)] = []
        group_dict_labeling['group'+str(i+1)] = []
    #print(group_dict)
    for i in range(len(dispath_information)-1):
        group_dict[str(dispath_information[i+1][2])].append(dispath_information[i+1][0])
        group_dict_grading[str(dispath_information[i+1][2])].append(dispath_information[i+1][0])
    
    for group in group_dict:
        #print(group)
        #print(group_dict[group])
        for i in range(len(group_dict[group])):
            original_video_name = group_dict[group][i]
            group_dict[group][i] = 'S_'+original_video_name
            group_dict_grading[group][i] = 'S_'+original_video_name
            group_dict[group].append('R_'+group_dict[group][i])

        #duplicate the videos list and shuffle them
        group_dict_labeling[group] = copy.deepcopy(group_dict[group])
        group_dict[group] = group_dict[group]*2    
        random.shuffle(group_dict[group])
    
    return group_dict, group_dict_grading, group_dict_labeling


def create_experiment_settings_for_one_group(group_name, group_videos):##################   
    #create 10 settings files for one group
    settings_list = []
    for i in range(10):
        settings_list.append(copy.deepcopy(settings_temp))
    #add 90 videos to each settings file
    
    sub_number = group_name[-1]

    for i in range(len(group_videos)):
        settings_list[i%10]['stimuli']['movie_files'].append(stimuli_path+group_videos[i])
    #write 10 settings files to disk
    for i in range(10): 
        with open(settings_folder_path+'/experiment_settings_'+'sub_'+sub_number+'_run_'+str(i+1)+'.yml', 'w') as outfile:
            print(settings_folder_path+'/experiment_settings_'+'sub_'+sub_number+'_run_'+str(i+1)+'.yml:')
            print(settings_list[i])
            print(' ')
            yaml.dump(settings_list[i], outfile, default_flow_style=False)

def create_experiment_settings_for_one_group_grading(group_name, group_videos):##################
    #create 10 settings files for one group
    settings_list = []
    for i in range(10):
        settings_list.append(copy.deepcopy(settings_temp))
    sub_number = group_name[-1]
    #add 90 videos to each settings file
    for i in range(len(group_videos)):
        settings_list[i%10]['stimuli']['movie_files'].append(stimuli_path+group_videos[i])
    #write 10 settings files to disk
    for i in range(10):
        with open(settings_folder_path+'/grading_experiment_settings_'+'sub_'+sub_number+'_run_'+str(i+1)+'.yml', 'w') as outfile:
            print(settings_folder_path+'/grading_experiment_settings_'+'sub_'+sub_number+'_run_'+str(i+1)+'.yml:')
            print(settings_list[i])
            print(' ')
            yaml.dump(settings_list[i], outfile, default_flow_style=False)

def create_experiment_settings_for_one_group_labeling(group_name, group_videos):##################
    #create 10 settings files for one group
    settings_list = []
    for i in range(10):
        settings_list.append(copy.deepcopy(settings_temp))
    #add 90 videos to each settings file
    sub_number = group_name[-1]
    for i in range(len(group_videos)):
        settings_list[i%10]['stimuli']['movie_files'].append(stimuli_path+group_videos[i])
    #write 10 settings files to disk
    for i in range(10):
        with open(settings_folder_path+'/labeling_experiment_settings_'+'sub_'+sub_number+'_run_'+str(i+1)+'.yml', 'w') as outfile:
            print(settings_folder_path+'/labeling_experiment_settings_'+'sub_'+sub_number+'_run_'+str(i+1)+'.yml:')
            print(settings_list[i])
            print(' ')
            yaml.dump(settings_list[i], outfile, default_flow_style=False) 



def create_settings_for_all_groups():
    group_dict, group_dict_grading, group_dict_labeling = organize_videos_by_group()
    for group in group_dict:
        create_experiment_settings_for_one_group(group, group_dict[group])
        create_experiment_settings_for_one_group_grading(group, group_dict_grading[group])
        create_experiment_settings_for_one_group_labeling(group, group_dict_labeling[group])


if __name__=='__main__':
    create_settings_for_all_groups()




    