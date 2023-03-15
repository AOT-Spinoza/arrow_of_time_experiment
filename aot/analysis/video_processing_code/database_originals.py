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
all_catagories_path = base_dir / core_settings["paths"]["stimuli_processing_path"] / "raws"
all_catagory_folders = os.listdir(all_catagories_path)

# make information list of (video_name, category_name, group_name, duration, width, height, size, frame_rate)


def get_information_list():
    all_catagories_names = copy.deepcopy(all_catagory_folders)
    # print(all_catagory_folders)

    information_list = []

    for i in range(len(all_catagory_folders)):
        category_folder = all_catagory_folders[i]
        # get rid of .DS_Store
        if category_folder.startswith("."):
            continue
        all_videos = [
            video
            for video in os.listdir(all_catagories_path / category_folder)
            if video.endswith(".mp4")
        ]
        # random_seed = random.randint(0,group_number-1)
        # print(all_videos)
        for j in range(len(all_videos)):
            # duration = ffmpeg.probe(all_catagories_path+'/'+category_folder+'/'+all_videos[j])['format']['duration']
            print(all_catagories_path / category_folder / all_videos[j])
            if (
                "h264"
                in ffmpeg.probe(
                    all_catagories_path / category_folder / all_videos[j]
                )["streams"][0]["codec_name"]
            ):
                width = ffmpeg.probe(
                    all_catagories_path / category_folder / all_videos[j]
                )["streams"][0]["width"]
                height = ffmpeg.probe(
                    all_catagories_path / category_folder / all_videos[j]
                )["streams"][0]["height"]
            if (
                "acc"
                in ffmpeg.probe(
                    all_catagories_path / category_folder / all_videos[j]
                )["streams"][0]["codec_name"]
            ):
                width = ffmpeg.probe(
                    all_catagories_path / category_folder / all_videos[j]
                )["streams"][1]["width"]
                height = ffmpeg.probe(
                    all_catagories_path / category_folder / all_videos[j]
                )["streams"][1]["height"]
            size = (
                os.path.getsize(
                    all_catagories_path / category_folder / all_videos[j]
                )
                / 1000000
            )
            frame_rate = ffmpeg.probe(
                all_catagories_path / category_folder / all_videos[j]
            )["streams"][0]["avg_frame_rate"]
            duration = ffmpeg.probe(
                all_catagories_path / category_folder / all_videos[j]
            )["format"]["duration"]

            # uniformly distribute the videos of each categories to different groups
            # group_index = ((j+random_seed)%group_number)+1############################

            # information_list.append((all_videos[j], all_catagories_names[i], 'group'+str(group_index), duration, width, height, size, frame_rate))
            information_list.append(
                (
                    all_videos[j],
                    all_catagories_names[i],
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
    print(all_catagory_folders)
    df = pd.DataFrame(
        information_list,
        columns=[
            "video_name",
            "category_name",
            "duration",
            "width",
            "height",
            "size",
            "frame_rate",
        ],
    )
    df.to_csv(base_dir / "data/videos/database_originals.tsv", sep="\t", index=False)

if __name__ == "__main__":
    information_list = get_information_list()
    save_list_to_tsv(information_list)
