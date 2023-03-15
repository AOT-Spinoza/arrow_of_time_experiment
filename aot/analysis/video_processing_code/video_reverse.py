import sys
import os
import pandas as pd
import ffmpeg
import yaml
from pathlib import Path
import aot

# get reversed video and save it reversed_videos folder for all groups
def reverse_video():
    base_dir = Path(aot.__path__[0])
    core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
    core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader) 


    stimuli_processing_path = Path(core_settings["paths"]["stimuli_processing_path"])
    category_path =  stimuli_processing_path / "raws"
    streched_path =  stimuli_processing_path / "resampled"
    reversed_path =  stimuli_processing_path / "reversed"
    # all_group_folders=[folder for folder in os.listdir(group_path) if folder.startswith('group')]
    all_streched_videos = [
        video for video in os.listdir(streched_path) if video.endswith(".mp4")
    ]

    for video in all_streched_videos:
        os.system(
            "ffmpeg -i "
            + str(streched_path)
            + "/"
            + video
            + " -c:v libx264"
            + " -preset veryslow"
            + " -crf 10"
            + " -vf reverse,fps=60"
            + " -an "
            + str(reversed_path)
            + "/"
            + "R_"
            + str(video)
        )


if __name__ == "__main__":
    reverse_video()
