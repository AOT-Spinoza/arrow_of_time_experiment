import sys
import os
import pandas as pd
import ffmpeg
import yaml
from pathlib import Path
import aot



# strech all videos into n seconds long and save them into stretched_videos folder
def stretch_video_n_seconds(n):

    base_dir = Path(aot.__path__[0])
    core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
    core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader)

    stimuli_processing_path = core_settings["paths"]["stimuli_processing_path"]
    category_path = base_dir / stimuli_processing_path / "raws"
    streched_path = base_dir / stimuli_processing_path / "resampled"
    # revmoe files that is not a folder
    all_categories_folder = [
        folder
        for folder in os.listdir(category_path)
        if os.path.isdir(category_path / folder)
    ]
    for category_folder in all_categories_folder:
        if os.path.isdir(category_path / category_folder):
            all_sub_content = os.listdir(category_path / category_folder)
            ###############################################
            for sub_content in all_sub_content:
                if sub_content.endswith(".mp4"):
                    # get video duration
                    probe = ffmpeg.probe(
                        str(category_path / category_folder / sub_content)
                    )
                    video_info = next(
                        s for s in probe["streams"] if s["codec_type"] == "video" 
                    )
                    duration = float(video_info["duration"])
                    time_ratio = n / duration
                    # get stretched video
                    os.system(
                        "ffmpeg -i "
                        + str(category_path)
                        + "/"
                        + str(category_folder)
                        + "/"
                        + str(sub_content)
                        + " -c:v libx264"
                        + " -preset veryslow"
                        + " -crf 10"
                        + " -vf setpts="
                        + str(time_ratio)
                        + "*PTS,fps=60"
                        + " -an "
                        + str(streched_path)
                        + "/"
                        + "S_"
                        + str(sub_content)
                    )


if __name__ == "__main__":
    stretch_video_n_seconds(2.5)
