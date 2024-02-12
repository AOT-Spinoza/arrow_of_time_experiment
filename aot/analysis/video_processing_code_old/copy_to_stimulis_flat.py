import os
import pandas as pd
import yaml
from pathlib import Path
import aot

base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader) 


stimuli_processing_path = Path(core_settings["paths"]["stimuli_processing_path"])
category_path =  stimuli_processing_path / "raws"
streched_path =  stimuli_processing_path / "resampled"
reversed_path =  stimuli_processing_path / "reversed"
flat_path =  Path(core_settings["paths"]["stimuli_path"])

all_streched_videos = [
    video for video in os.listdir(streched_path) if video.endswith(".mp4")
]
all_reversed_videos = [
    video for video in os.listdir(reversed_path) if video.endswith(".mp4")
]

if __name__ == "__main__": 
    for video in all_streched_videos:
        os.system("cp " + str(streched_path / video) + " " + str(flat_path / video))
    for video in all_reversed_videos:
        os.system("cp " + str(reversed_path / video) + " " + str(flat_path / video))
