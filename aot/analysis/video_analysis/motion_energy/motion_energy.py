import moten
import pickle
import yaml
import os
import aot
from pathlib import Path
import aot.analysis.video_processing_code.database_append as db_append


base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
core_settings = yaml.load(
    open(core_expt_yaml_path, "r"), Loader=yaml.FullLoader)
stimuli_path = Path(core_settings["paths"]["stimuli_path"])

result_path = base_dir / "analysis/video_analysis/motion_energy/result"


def get_motion_energy(video_file):
    luminance_images = moten.io.video2luminance(video_file)

    # Create a pyramid of spatio-temporal gabor filters
    nimages, vdim, hdim = luminance_images.shape
    print(nimages, vdim, hdim)
    pyramid = moten.get_default_pyramid(vhsize=(vdim, hdim), fps=24)

    # Compute motion energy features
    moten_features = pyramid.project_stimulus(luminance_images)
    print(moten_features)
    print(moten_features.shape)

    return moten_features


def check_result_existence(video):
    if (result_path / f"{video}.pkl").exists():
        print(f"Already processed: {video}")
        return True
    else:
        # print(f"Processing: {video}")
        return False


all_videos = [video for video in os.listdir(
    stimuli_path) if video.endswith(".mp4")]


for video in all_videos:
    if check_result_existence(video):
        continue
    else:
        print(video)
        moten_features = get_motion_energy(str(stimuli_path / video))
        pickle.dump(moten_features, open(result_path / f"{video}.pkl", "wb"))
