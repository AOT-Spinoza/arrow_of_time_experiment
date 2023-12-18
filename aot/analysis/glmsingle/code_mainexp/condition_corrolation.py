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
    print("timepoints_indexs:", timepoints_indexs.shape)
    timepoints_indexs = np.where(timepoints_indexs == 1)[0]
    print("timepoints_indexs:", timepoints_indexs)
    return timepoints_indexs


def get_corrolation_maps(design, betas):  # return a array of [n_conditions, x,y,z]
    corrolation_maps = []
    for condition_index in range(design.shape[1]):
        timepoints_indexs = condition_to_timepoints(condition_index, design)
        timepoints_betas = betas[:, :, :, timepoints_indexs]
        print("timepoints_betas:", timepoints_betas.shape)
        mapshape = timepoints_betas.shape[:-1]
        print("mapshape:", mapshape)
        # timepoints_betas = timepoints_betas.reshape(-1,2)
        # print("timepoints_betas:", timepoints_betas.shape)
        # calculate the corrolation map (x,y,z) for each condition and each voxel
        corrolation_map = np.zeros(mapshape)
        for x in range(mapshape[0]):
            for y in range(mapshape[1]):
                for z in range(mapshape[2]):
                    corr_pair = timepoints_betas[x, y, z, :].T
                    # print("corr_pair shape:", corr_pair.shape)
                    # print("corr_pair:", corr_pair)
                    # corr_value = np.corrcoef(timepoints_betas[x,y,z,:])#[0,1]         this would be meaningless
                    diff = np.diff(corr_pair)
                    # print("corr_value:", corr_value)
                    corr_value = 1 / np.abs(diff)
                    corrolation_map[x, y, z] = corr_value

        print("corrolation_map:", corrolation_map.shape)
        corrolation_maps.append(corrolation_map)
    corrolation_maps = np.array(corrolation_maps)
    print("corrolation_maps:", corrolation_maps.shape)
    return corrolation_maps


def test():
    # get the design for one session
    design_sample = index_to_cleaned_design(2, 1)
    test_glm_file = "/tank/shared/2022/arrow_of_time/arrow_of_time_exp/aot/analysis/glmsingle/outputs/mainexp/sub-002_ses-01_T1W_nofmriprepstc/TYPEC_FITHRF_GLMDENOISE.npy"
    betas = load_betas(test_glm_file)
    corrolation_maps = get_corrolation_maps(design_sample, betas)
    print("corrolation_maps:", corrolation_maps.shape)
    # save the corrolation maps
    savefile = "/tank/shared/2022/arrow_of_time/arrow_of_time_exp/aot/analysis/glmsingle/outputs/mainexp/sub-002_ses-01_T1W_nofmriprepstc/TYPEC_FITHRF_GLMDENOISE/corrolation_maps.nii"
    #save as nifti
    data = corrolation_maps
    data = nib.Nifti1Image(data, np.eye(4))
    nib.save(data, savefile)


test()
