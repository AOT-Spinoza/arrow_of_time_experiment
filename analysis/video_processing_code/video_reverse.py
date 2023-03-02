import sys
import os
import pandas as pd
import ffmpeg
import yaml

#get reversed video and save it reversed_videos folder for all groups
def reverse_video(n):
    base_settings  = yaml.load(open('base_settings.yaml'), Loader=yaml.FullLoader)
    rootpath = base_settings['path']['rootpath']
    streched_path = rootpath+base_settings['path']['streched_path']
    reversed_path = rootpath+base_settings['path']['reversed_path']
    #all_group_folders=[folder for folder in os.listdir(group_path) if folder.startswith('group')]
    all_streched_videos = [video for video in os.listdir(streched_path) if video.endswith('.mp4')]

    for video in all_streched_videos:
        os.system('ffmpeg -i '+streched_path+'/'+video+' -c:v libx264'+' -preset veryslow'+' -crf 10'+' -vf reverse,fps=60'+' -an '+reversed_path+'/'+'R_'+video)

if __name__=='__main__':
    reverse_video(2)
