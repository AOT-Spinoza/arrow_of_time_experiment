import numpy as np
import nibabel as nib
import os
import sys
import pandas as pd
import yaml
from pathlib import Path
from glmsingle.glmsingle import GLM_single
import copy
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

gimsingle_output_root = base_dir / "analysis/glmsingle/outputs/mainexp"
design_output_root = base_dir / "analysis/glmsingle/outputs/design"


def clean_design_time(design):
    # remove all the blank rows
    new_design = []
    for row in design:
        if np.sum(row) > 0:
            new_design.append(row)
    new_design = np.array(new_design)
    print(new_design.shape)
    return new_design


def clean_design_condition(design):
    # reomve all the blank cloumns
    new_design = []
    for col in design.T:
        if np.sum(col) > 0:
            new_design.append(col)
    new_design = np.array(new_design).T
    print(new_design.shape)
    return new_design


def index_to_cleaned_design(sub, ses):
    def index_to_design_output(sub, ses, run):
        sub = str(sub).zfill(2)
        ses = str(ses).zfill(2)
        run = str(run).zfill(2)
        target_path = design_output_root / f"design_sub_{sub}_ses_{ses}_run_{run}.npy"
        return target_path

    list_of_designs = []
    for run in range(1, run_number + 1):
        design_file = index_to_design_output(sub, ses, run)
        design = np.load(design_file, allow_pickle=True)
        print(design.shape)
        list_of_designs.append(design)
    session_design = np.concatenate(list_of_designs, axis=0)
    session_design = clean_design_time(session_design)
    session_design = clean_design_condition(session_design)

    print("cleaned design shape:", session_design.shape)
    return session_design


def load_betas(glmoutputfile):
    test_data = np.load(glmoutputfile, allow_pickle=True).item()
    betas = test_data["betasmd"]
    print("shape of betas:", betas.shape)
    return betas


def condition_to_timepoints(condition_index, design):
    timepoints_indexs = design[:, condition_index]
    # print("timepoints_indexs:", timepoints_indexs.shape)
    timepoints_indexs = np.where(timepoints_indexs == 1)[0]
    # print("timepoints_indexs:", timepoints_indexs)
    return timepoints_indexs


def get_correlation_maps(design, betas):  # return a array of [x,y,z]
    corrolation_map = np.zeros((betas.shape[0], betas.shape[1], betas.shape[2]))
    betas_shape = betas.shape  # [x,y,z,t]
    # iterate over voxels
    for x in range(betas_shape[0]):
        for y in range(betas_shape[1]):
            for z in range(betas_shape[2]):
                voxel_betas = betas[x, y, z, :]
                voxel_points_for_corrolation = []
                # iterate over conditions
                for condition_index in range(design.shape[1]):
                    timepoints_indexs = condition_to_timepoints(condition_index, design)
                    condition_betas = voxel_betas[
                        timepoints_indexs
                    ]  # should be the condition beta for one sinlge voxel
                    voxel_points_for_corrolation.append(condition_betas)
                voxel_points_for_corrolation = np.array(
                    voxel_points_for_corrolation
                ).T  ##########################################################################################
                # print("voxel_points_for_corrolation:", voxel_points_for_corrolation.shape)
                # calculate corrolation
                corrolation = np.corrcoef(voxel_points_for_corrolation)[0, 1]
                corrolation_map[x, y, z] = corrolation
    return corrolation_map


def test():
    # get the design for one session
    design_sample = index_to_cleaned_design(2, 1)
    print("design_sample:", design_sample.shape)
    test_glm_file = "/tank/shared/2022/arrow_of_time/arrow_of_time_exp/aot/analysis/glmsingle/outputs/mainexp/sub-002_ses-01_T1W_nofmriprepstc/TYPED_FITHRF_GLMDENOISE_RR.npy"
    betas = load_betas(test_glm_file)
    corrolation_maps = get_correlation_maps(design_sample, betas)
    print("corrolation_maps:", corrolation_maps.shape)
    # save the corrolation maps
    savefile = "/tank/shared/2022/arrow_of_time/arrow_of_time_exp/aot/analysis/glmsingle/outputs/mainexp/sub-002_ses-01_T1W_nofmriprepstc/TYPED_FITHRF_GLMDENOISE_RR/correlation_maps.nii"
    # save as nifti
    data = corrolation_maps
    data = nib.Nifti1Image(data, np.eye(4))
    nib.save(data, savefile)


def test2():
    # get the design for one session
    design_sample = index_to_cleaned_design(1, 1)
    print("design_sample:", design_sample.shape)
    test_glm_file = "/tank/shared/2022/arrow_of_time/arrow_of_time_exp/aot/analysis/glmsingle/outputs/mainexp/sub-001_ses-01_T1W_nofmriprepstc/TYPED_FITHRF_GLMDENOISE_RR.npy"
    betas = load_betas(test_glm_file)
    corrolation_maps = get_correlation_maps(design_sample, betas)
    print("corrolation_maps:", corrolation_maps.shape)
    # save the corrolation maps
    savefile = "/tank/shared/2022/arrow_of_time/arrow_of_time_exp/aot/analysis/glmsingle/outputs/mainexp/sub-001_ses-01_T1W_nofmriprepstc/TYPED_FITHRF_GLMDENOISE_RR/correlation_maps.nii"
    # save as nifti
    data = corrolation_maps
    data = nib.Nifti1Image(data, np.eye(4))
    nib.save(data, savefile)


test()
test2()
