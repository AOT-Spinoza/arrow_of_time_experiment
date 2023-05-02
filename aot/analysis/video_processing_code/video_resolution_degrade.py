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
        if (
            "h264"
            in probe["streams"][0]["codec_name"]
        ):
            width = ffmpeg.probe(str(stimuli_path / video)
                                 )["streams"][0]["width"]
            height = ffmpeg.probe(str(stimuli_path / video)
                                  )["streams"][0]["height"]
        elif (
            "acc"
            in probe["streams"][0]["codec_name"]
        ):
            width = ffmpeg.probe(str(stimuli_path / video)
                                 )["streams"][1]["width"]
            height = ffmpeg.probe(str(stimuli_path / video)
                                  )["streams"][1]["height"]

        width_degraded = width // n
        height_degraded = height // n

        os.system("ffmpeg -i " + str(stimuli_path / video) + " -vf scale=" + str(width_degraded) +
                  ":" + str(height_degraded) + " " + str(target_stimuli_degraded_path / video))


if __name__ == "__main__":
    degrade_resolution_t_times(4)
