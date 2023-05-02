import os
import pickle
import yaml
import aot
import ffmpeg
from pathlib import Path


def degrade_resolution_t_times(n):
    base_dir = Path(aot.__path__[0])
    core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
    core_settings = yaml.load(
        open(core_expt_yaml_path), Loader=yaml.FullLoader)

    stimuli_path = Path(core_settings["paths"]["stimuli_path"])
    target_stimuli_degraded_path = Path(
        core_settings["paths"]["stimuli_degraded_path"])

    # degrade the resolution of all videos into n times (width and height both decrease n times)
    all_videos = [video for video in os.listdir(
        stimuli_path) if video.endswith(".mp4")]

    for video in all_videos:
        probe = ffmpeg.probe(str(stimuli_path / video))
        video_info = next(
            s for s in probe["streams"] if s["codec_type"] == "video")
        width = int(video_info["width"])
        height = int(video_info["height"])
        os.system(
            "ffmpeg -i "
            + str(stimuli_path)
            + "/"
            + str(video)
            + " -vf scale="
            + str(int(width/n))
            + ":"
            + str(int(height/n))
            + " "
            + str(target_stimuli_degraded_path)
            + "/"
            + str(video)
        )


if __name__ == "__main__":
    degrade_resolution_t_times(4)
