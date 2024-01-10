import os
import sys
import numpy as np
import nibabel as nib
from pathlib import Path
import pandas as pd
import yaml
import aot

base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
stimuli_temp_path = base_dir / "experiment/stimuli_settings_temp.yml"
core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader)
stimuli_settings_temp = yaml.load(open(stimuli_temp_path), Loader=yaml.FullLoader)
settings_root_path = base_dir / core_settings["paths"]["settings_path"]
video_db_path = base_dir / "data/videos/database_originals.tsv"
video_db = pd.read_csv(video_db_path, sep="\t")
run_number = core_settings["various"]["run_number"]

glmsingle_output_root = base_dir / "analysis/glmsingle/outputs/mainexp"
stack_output_root = base_dir / "analysis/glmsingle/outputs/temp/shiftstack"

shifts = [-5,-4, -3, -2, -1, 0, 1, 2]


def shift_num_to_reversedstc_output(shift_num):
    target_path = (
        glmsingle_output_root
        / ("sub-002_ses-01_T1W_nofmriprepstc_reversedstc_shift_" + str(shift_num))
        / "TYPED_FITHRF_GLMDENOISE_RR.npy"
    )
    return target_path


def shift_num_to_nonreversedstc_output(shift_num):
    target_path = (
        glmsingle_output_root
        / ("sub-002_ses-01_T1W_nofmriprepstc_shift_" + str(shift_num))
        / "TYPED_FITHRF_GLMDENOISE_RR.npy"
    )
    return target_path


def stack_all_reversedstc_output():
    stack = []
    for shift in shifts:
        target_path = shift_num_to_reversedstc_output(shift)
        R2_data = np.load(target_path, allow_pickle=True).item()["R2"]
        print(R2_data.shape)
        stack.append(R2_data)
    stack = np.stack(stack, axis=3)
    print(stack.shape)
    # save the stack as a nifti
    stack = nib.Nifti1Image(stack, np.eye(4))
    nib.save(stack, stack_output_root / "reversedstc_stack.nii")


def stack_all_nonreversedstc_output():
    stack = []
    for shift in shifts:
        target_path = shift_num_to_nonreversedstc_output(shift)
        R2_data = np.load(target_path, allow_pickle=True).item()["R2"]
        print(R2_data.shape)
        stack.append(R2_data)
    stack = np.stack(stack, axis=3)
    print(stack.shape)
    # save the stack as a nifti
    stack = nib.Nifti1Image(stack, np.eye(4))
    nib.save(stack, stack_output_root / "nonreversedstc_stack.nii")


def stack_all_difference_output():
    stack = []
    for shift in shifts:
        target_path_reversestc = shift_num_to_reversedstc_output(shift)
        target_path_nonreversestc = shift_num_to_nonreversedstc_output(shift)
        R2_data_reversedstc = np.load(target_path_reversestc, allow_pickle=True).item()["R2"]
        R2_data_nonreversedstc = np.load(target_path_nonreversestc, allow_pickle=True).item()["R2"]
        R2_data_difference = R2_data_reversedstc - R2_data_nonreversedstc
        print(R2_data_difference.shape)
        stack.append(R2_data_difference)
    stack = np.stack(stack, axis=3)
    print(stack.shape)
    # save the stack as a nifti
    stack = nib.Nifti1Image(stack, np.eye(4))
    nib.save(stack, stack_output_root / "difference_stack.nii")


if __name__ == "__main__":
    stack_all_reversedstc_output()
    stack_all_nonreversedstc_output()
    stack_all_difference_output()
