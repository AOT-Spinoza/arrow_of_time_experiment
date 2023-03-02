import sys
import os
import pandas as pd
import ffmpeg
import copy
import random
import yaml


#get the category path from the csv file
settings_temp = yaml.load(open('base_settings.yaml'), Loader=yaml.FullLoader)
rootpath = settings_temp['path']['rootpath']
settings_folder_path = rootpath+settings_temp['path']['settings_path']
stimuli_path = rootpath+settings_temp['path']['stimuli_path']
all_catagories_path = rootpath+settings_temp['path']['category_path']
all_catagory_folders=os.listdir(all_catagories_path)


#read group number from settings_template.yml
group_number = settings_temp['various']['group_number']


#make information list of (video_name, category_name, group_name, duration, width, height, size, frame_rate)   
def get_information_list():  
    all_catagories_names = copy.deepcopy(all_catagory_folders)
    information_list = []

    for i in range(len(all_catagory_folders)):
        category_folder = all_catagory_folders[i]
        #get rid of .DS_Store
        if category_folder.startswith('.'):
            continue
        all_videos = [video for video in os.listdir(all_catagories_path+'/'+category_folder) if video.endswith('.mp4')]
        random_seed = random.randint(0,group_number-1)
        #print(all_videos)
        for j in range(len(all_videos)):
 
            group_index = ((j+random_seed)%group_number)+1############################


            #information_list.append((all_videos[j], all_catagories_names[i], 'group'+str(group_index), duration, width, height, size, frame_rate))
            information_list.append((all_videos[j], all_catagories_names[i], 'group'+str(group_index)))
    return information_list
    
#save the information list to csv, local path

#save the information list to tsv, local path      
def save_list_to_tsv(information_list):
    print(all_catagory_folders)

    #save the information list to csv
    #df = pd.DataFrame(information_list, columns=['video_name', 'category_name', 'group_name', 'duration', 'width', 'height', 'size', 'frame_rate'])
    df = pd.DataFrame(information_list, columns=['video_name', 'category_name', 'group_name'])
    df.to_csv('video_dispatch.tsv', sep='\t', index=False)



if __name__=='__main__':
    #get the information list
    information_list = get_information_list()
    #save the information list to csv
    save_list_to_tsv(information_list)










