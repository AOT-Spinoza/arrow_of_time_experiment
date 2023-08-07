import os
import argparse
import yaml
import aot
from pathlib import Path

base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader) 
flat_path =  Path(core_settings["paths"]["stimuli_path"])
pictures_path = Path(core_settings["paths"]["stimuli_picture_path"])

#save the middle frame of each video as a picture
def video_to_pic(video_path):
    video_name = video_path.stem
    os.system("ffmpeg -i " + str(video_path) + " -ss 00:00:01.000 -vframes 1 " + str(pictures_path / video_name) + ".png")

if __name__ == "__main__":
    for video in os.listdir(flat_path):
        if video.endswith(".mp4"):
            video_to_pic(flat_path / video)


    