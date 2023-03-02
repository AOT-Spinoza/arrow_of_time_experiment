import os
import pandas as pd
import yaml

base_settings  = yaml.load(open('base_settings.yaml'), Loader=yaml.FullLoader)
rootpath = base_settings['path']['rootpath']
streched_path = rootpath+base_settings['path']['streched_path']
category_path = rootpath+base_settings['path']['category_path']
streched_path =  rootpath + base_settings['path']['streched_path']
reversed_path =  rootpath + base_settings['path']['reversed_path']
flat_path =  rootpath + base_settings['path']['stimuli_path']

all_streched_videos = [video for video in os.listdir(streched_path) if video.endswith('.mp4')]
all_reversed_videos = [video for video in os.listdir(reversed_path) if video.endswith('.mp4')]

if __name__=='__main__':
    for video in all_streched_videos:
        os.system('cp '+streched_path+video+' '+flat_path+video)
    for video in all_reversed_videos:
        os.system('cp '+reversed_path+video+' '+flat_path+video)

