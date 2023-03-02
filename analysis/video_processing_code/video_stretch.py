import sys
import os
import pandas as pd
import ffmpeg
import yaml


#strech all videos into n seconds long and save them into stretched_videos folder
def stretch_video_n_seconds(n): 
    #load path from csv 
    #group_path =  pd.read_csv('path.csv', header=None, index_col=0).loc['group_path'][1]
    base_settings  = yaml.load(open('base_settings.yaml'), Loader=yaml.FullLoader)
    rootpath = base_settings['path']['rootpath']
    streched_path = rootpath+base_settings['path']['streched_path']
    category_path = rootpath+base_settings['path']['category_path']
    #all_group_folders=[folder for folder in os.listdir(group_path) if folder.startswith('group')]
    #revmoe files that is not a folder
    all_categories_folder = [folder for folder in os.listdir(category_path) if os.path.isdir(category_path+'/'+folder)]
    for category_folder in all_categories_folder:
        if os.path.isdir(category_path+'/'+category_folder):
            all_sub_content=os.listdir(category_path+'/'+category_folder)
            ###############################################
            for sub_content in all_sub_content:
                if sub_content.endswith('.mp4'): 
                    #get video duration
                    probe = ffmpeg.probe(category_path+'/'+category_folder+'/'+sub_content)
                    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
                    duration = float(video_info['duration'])
                    time_ratio = n/duration
                    #get stretched video
                    os.system('ffmpeg -i '+category_path+category_folder+'/'+sub_content+' -c:v libx264'+' -preset veryslow'+' -crf 10'+' -vf setpts='+str(time_ratio)+'*PTS,fps=60'+' -an '+streched_path+'/'+'S_'+sub_content) 


if __name__=='__main__':
    stretch_video_n_seconds(2.5)
    

