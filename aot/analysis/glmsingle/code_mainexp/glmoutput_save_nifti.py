import os
import sys
import numpy as np
import nibabel as nib
from pathlib import Path
import pandas as pd
import yaml
import aot

# from aot.analysis.glmsingle.code_mainexp.condition_corrolation import *

base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
stimuli_temp_path = base_dir / "experiment/stimuli_settings_temp.yml"
core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader)
stimuli_settings_temp = yaml.load(open(stimuli_temp_path), Loader=yaml.FullLoader)
settings_root_path = base_dir / core_settings["paths"]["settings_path"]
video_db_path = base_dir / "data/videos/database_originals.tsv"
video_db = pd.read_csv(video_db_path, sep="\t")
run_number = core_settings["various"]["run_number"]

gimsingle_output_root = base_dir / "analysis/glmsingle/outputs/mainexp"
design_output_root = base_dir / "analysis/glmsingle/outputs/design"


def save_niftis_for_one_folder(gim_output_folder):
    def save_nifti_for_one_type(file):  # input is a complete path to a file
        # make a folder for this type of nifti with the same name as the file but without the .npy
        save_folder_path = str(file).split(".")[0]
        if os.path.exists(save_folder_path):
            pass
        else:
            os.makedirs(save_folder_path)

        test_data = np.load(file, allow_pickle=True).item()
        for key in test_data:
            print(key)
            # save the nifti file as key name in the folder
            nifti_file_name = save_folder_path + "/" + key + ".nii"
            print(nifti_file_name)
            data = test_data[key]
            # make the data nifti
            try:
                data = nib.Nifti1Image(data, np.eye(4))
                nib.save(data, nifti_file_name)
            except:
                print(
                    "error saving nifti file: " + nifti_file_name + " for key: " + key
                )

    # get all the files in the folder
    filenames = [
        "TYPEA_ONOFF.npy",
        "TYPEB_FITHRF.npy",
        "TYPEC_FITHRF_GLMDENOISE.npy",
        "TYPED_FITHRF_GLMDENOISE_RR.npy",
    ]
    for file in filenames:
        file = gim_output_folder / file
        save_nifti_for_one_type(file)
        try: 
            save_nifti_for_one_type(file)
        except:
            print("error saving niftis for file: " + str(file))

def save_niftis_for_all_folders(root_folder):
    # get all the folders in the root folder
    folders = os.listdir(root_folder)
    for folder in folders:
        folder = root_folder / folder
        save_niftis_for_one_folder(folder)


if __name__ == "__main__":
    save_niftis_for_all_folders(gimsingle_output_root) 
    