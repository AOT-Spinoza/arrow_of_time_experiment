import sys
import os
import pandas as pd
import ffmpeg
import copy
import random
import yaml
import aot
from pathlib import Path


base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
core_settings = yaml.load(open(core_expt_yaml_path, "r"), Loader=yaml.FullLoader)
stimuli_path = Path(core_settings["paths"]["stimuli_path"])


def get_information_list():
    information_list = []

    all_videos = [video for video in os.listdir(stimuli_path) if video.endswith(".mp4")]
    # random_seed = random.randint(0,group_number-1)
    # print(all_videos)
    for j in range(len(all_videos)):
        # duration = ffmpeg.probe(all_catagories_path+'/'+category_folder+'/'+all_videos[j])['format']['duration']
        print(stimuli_path / all_videos[j])
        if (
            "h264"
            in ffmpeg.probe(stimuli_path / all_videos[j])["streams"][0]["codec_name"]
        ):
            width = ffmpeg.probe(stimuli_path / all_videos[j])["streams"][0]["width"]
            height = ffmpeg.probe(stimuli_path / all_videos[j])["streams"][0]["height"]
        if (
            "acc"
            in ffmpeg.probe(stimuli_path / all_videos[j])["streams"][0]["codec_name"]
        ):
            width = ffmpeg.probe(stimuli_path / all_videos[j])["streams"][1]["width"]
            height = ffmpeg.probe(stimuli_path / all_videos[j])["streams"][1]["height"]
        size = os.path.getsize(stimuli_path / all_videos[j]) / 1000000
        frame_rate = ffmpeg.probe(stimuli_path / all_videos[j])["streams"][0][
            "avg_frame_rate"
        ]

        duration = ffmpeg.probe(stimuli_path / all_videos[j])["format"]["duration"]

        # uniformly distribute the videos of each categories to different groups
        # group_index = ((j+random_seed)%group_number)+1############################

        # information_list.append((all_videos[j], all_catagories_names[i], 'group'+str(group_index), duration, width, height, size, frame_rate))
        information_list.append(
            (
                all_videos[j],
                duration,
                width,
                height,
                size,
                frame_rate,
            )
        )
    return information_list


# save the information list to tsv, local path


def save_list_to_tsv(information_list):
    df = pd.DataFrame(
        information_list,
        columns=[
            "video_name",
            "duration",
            "width",
            "height",
            "size",
            "frame_rate",
        ],
    )
    df.to_csv(base_dir / "data/videos/database_stimulus.tsv", sep="\t", index=False)


if __name__ == "__main__":
    information_list = get_information_list()
    save_list_to_tsv(information_list)
