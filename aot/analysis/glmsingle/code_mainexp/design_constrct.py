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
from aot.analysis.glmsingle.code_mainexp.glmoutput_save_nifti import (
    save_niftis_for_one_folder,
)

base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
stimuli_temp_path = base_dir / "experiment/stimuli_settings_temp.yml"
core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader)
stimuli_settings_temp = yaml.load(open(stimuli_temp_path), Loader=yaml.FullLoader)
settings_root_path = base_dir / core_settings["paths"]["settings_path"]
run_number = core_settings["various"]["run_number"]
total_video_number = core_settings["various"]["total_video_number"]


bold_data_root = "/tank/shared/2024/visual/AOT/derivatives/fmripreps/aotfull_preprocs/fullpreproc_forcesyn_endfix"
bold_data_root_nonnordic = "/tank/shared/2024/visual/AOT/derivatives/fmripreps/aotfull_preprocs/fullpreproc_nonnordic"
output_root = "/tank/shared/2024/visual/AOT/derivatives/glmsingle/mainexp"

design_output_root = "/tank/shared/2024/visual/AOT/derivatives/glmsingle/mainexp/design"


def movie_conditions_dict():  # include blank condition as 0
    total_video_names = []
    for i in range(1, total_video_number + 1):
        total_video_names.append(str(i).zfill(4) + "_fw.mp4")
        total_video_names.append(str(i).zfill(4) + "_rv.mp4")

    movies_conditions = {}
    # condnum = 0
    condnum = (
        -1
    )  # now the blank condition is -1 , every other condition(movie) is a non-negative number which could be used as index
    movies_conditions["blank"] = condnum
    for i in range(len(total_video_names)):
        if (
            total_video_names[i] not in movies_conditions
            and total_video_names[i] != "blank"
        ):
            condnum += 1
            movies_conditions[total_video_names[i]] = condnum
    print("total videos number: ", len(total_video_names))
    print(movies_conditions)
    video_condition_file_path = base_dir / "data/videos/video_conditions.tsv"
    video_condition_file = open(video_condition_file_path, "w")
    for key in movies_conditions.keys():
        video_condition_file.write(key + "\t" + str(movies_conditions[key]) + "\n")
    video_condition_file.close()

    return movies_conditions


movie_conditions = movie_conditions_dict()


def construct_design_from_exp_design_yml(ymlfile, movies_conditions, shift=0):
    BLANK = -1
    # read in the experiment design yaml file
    settings_sample = yaml.load(open(ymlfile), Loader=yaml.FullLoader)
    # get the movie files
    movies = settings_sample["stimuli"]["movie_files"]
    original_condition_list = [movies_conditions[movie] for movie in movies]
    # add blank condition to each element in the list
    original_condition_list = [
        [x] + [BLANK, BLANK, BLANK] for x in original_condition_list
    ]
    # flatten the list
    original_condition_list = [
        item for sublist in original_condition_list for item in sublist
    ]
    # add 16 0s to the start and end of the list
    original_condition_list = (
        [BLANK] * (16 + shift) + original_condition_list + [BLANK] * (16 - shift)
    )
    print(original_condition_list)
    print("desing len:", len(original_condition_list))
    # construct the design matrix from the condition list (one-hot encoding)

    design_matrix = np.zeros((len(original_condition_list), len(movies_conditions)))
    for i in range(len(original_condition_list)):
        if original_condition_list[i] != BLANK:
            design_matrix[i][original_condition_list[i]] = 1

    return design_matrix


def index_to_exp_yml(sub, ses, run):
    sub = str(sub).zfill(2)
    ses = str(ses).zfill(2)
    run = str(run).zfill(2)
    target_path = (
        settings_root_path
        / "main"
        / f"experiment_settings_sub_{sub}_ses_{ses}_run_{run}.yml"
    )
    return target_path


def index_to_design_output(sub, ses, run):
    sub = str(sub).zfill(2)
    ses = str(ses).zfill(2)
    run = str(run).zfill(2)
    target_path = design_output_root + "/" + f"design_sub_{sub}_ses_{ses}_run_{run}.npy"
    return target_path


def construct_design_for_one_run(sub, ses, run, shift=0):
    target_path = index_to_exp_yml(sub, ses, run)
    newdesign = construct_design_from_exp_design_yml(
        target_path, movie_conditions, shift
    )
    save_path = index_to_design_output(sub, ses, run)
    np.save(save_path, newdesign)
    return newdesign


def construct_design_for_one_session(sub, ses, shift=0):
    list_of_designs = []
    for run in range(1, run_number + 1):
        list_of_designs.append(construct_design_for_one_run(sub, ses, run, shift))
    return list_of_designs


def index_to_bold_data_fsaverage(sub, ses, run):  # input: int,int,int
    # sample :/tank/shared/2022/arrow_of_time/aotfull_preprocs/fullpreproc3/sub-001/ses-01/func/sub-001_ses-01_task-AOT_run-1_space-fsaverage_hemi-L_bold.func.gii
    sub = str(sub)
    ses = str(ses)
    run = str(run)
    Left_bold_path = (
        bold_data_root
        + "/"
        + "sub-"
        + sub.zfill(3)
        + "/ses-"
        + ses.zfill(2)
        + "/func/"
        + "sub-"
        + sub.zfill(3)
        + "_ses-"
        + ses.zfill(2)
        + "_task-AOT_run-"
        + run
        + "_space-fsaverage_hemi-L_bold.func.gii"
    )
    Right_bold_path = (
        bold_data_root
        + "/"
        + "sub-"
        + sub.zfill(3)
        + "/ses-"
        + ses.zfill(2)
        + "/func/"
        + "sub-"
        + sub.zfill(3)
        + "_ses-"
        + ses.zfill(2)
        + "_task-AOT_run-"
        + run
        + "_space-fsaverage_hemi-R_bold.func.gii"
    )
    # load and concatenate the bold data from left and right hemispheres
    img_L = nib.load(Left_bold_path)
    img_data_L = [x.data for x in img_L.darrays]
    cur_data_L = np.array(img_data_L)  # [0]
    # swap the first two dimensions#########################################maybe need to change
    cur_data_L = np.swapaxes(cur_data_L, 0, 1)
    print("bold data shape:", cur_data_L.shape)
    img_R = nib.load(Right_bold_path)
    img_data_R = [x.data for x in img_R.darrays]
    cur_data_R = np.array(img_data_R)  # [0]
    cur_data_R = np.swapaxes(cur_data_R, 0, 1)
    print("bold data shape:", cur_data_R.shape)
    cur_data = np.concatenate((cur_data_L, cur_data_R), axis=0)
    print("bold data shape:", cur_data.shape)
    return cur_data


def index_to_bold_data_T1W(sub, ses, run, nordictype="nordicstc"):  # input: int,int,int
    # sample : /tank/shared/2022/arrow_of_time/aotfull_preprocs/fullpreproc3/sub-001/ses-01/func/sub-001_ses-01_task-AOT_run-1_space-T1w_desc-preproc_bold.nii.gz
    sub = str(sub)
    ses = str(ses)
    run = str(run)
    if nordictype == "nordicstc":
        bold_path = (
            bold_data_root
            + "/"
            + "sub-"
            + sub.zfill(3)
            + "/ses-"
            + ses.zfill(2)
            + "/func/"
            + "sub-"
            + sub.zfill(3)
            + "_ses-"
            + ses.zfill(2)
            + "_task-AOT_rec-nordicstc_run-"
            + run
            + "_space-T1w_desc-preproc_part-mag_bold.nii.gz"
        )
    elif nordictype == "nonnordicstc":
        bold_path = (
            bold_data_root_nonnordic
            + "/"
            + "sub-"
            + sub.zfill(3)
            + "/ses-"
            + ses.zfill(2)
            + "/func/"
            + "sub-"
            + sub.zfill(3)
            + "_ses-"
            + ses.zfill(2)
            + "_task-AOT_rec-nonnordicstc_run-"
            + run
            + "_space-T1w_desc-preproc_part-mag_bold.nii.gz"
        )
    img = nib.load(bold_path)
    img_data = img.get_fdata()
    print("bold data shape:", img_data.shape)
    return img_data


def construct_bold_for_one_session(
    sub, ses, datatype, nordictype="nordicstc"
):  # fsnative or §T1W
    list_of_bold_data = []
    if datatype == "fsaverage":
        for run in range(1, run_number + 1):
            list_of_bold_data.append(index_to_bold_data_fsaverage(sub, ses, run))
        return list_of_bold_data
    elif datatype == "T1W":
        for run in range(1, run_number + 1):
            list_of_bold_data.append(index_to_bold_data_T1W(sub, ses, run, nordictype))
        return list_of_bold_data


def merge_bold_data(
    test_bold_file_L, test_bold_file_R
):  # directly from old, maybe need some change
    img_L = nib.load(test_bold_file_L)
    img_data_L = [x.data for x in img_L.darrays]
    cur_data_L = img_data_L[0]
    # swap the first two dimensions
    cur_data_L = np.swapaxes(cur_data_L, 0, 1)
    print("bold data shape:", cur_data_L.shape)
    img_R = nib.load(test_bold_file_R)
    img_data_R = [x.data for x in img_R.darrays]
    cur_data_R = img_data_R[0]
    cur_data_R = np.swapaxes(cur_data_R, 0, 1)
    print("bold data shape:", cur_data_R.shape)
    cur_data = np.concatenate((cur_data_L, cur_data_R), axis=0)
    print("bold data shape:", cur_data.shape)
    return cur_data


def construct_output_dir(
    sub, ses, data_type="T1W", nordictype="nordicstc", suffix=""
):  # input: int,int
    output_dir = (
        output_root
        + "/"
        + "sub-"
        + str(sub).zfill(3)
        + "_ses-"
        + str(ses).zfill(2)
        + "_"
        + data_type
        + "_"
        + nordictype
        + "_"
        + suffix
    )
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def construct_figuredir(
    sub, ses, data_type="T1W", nordictype="nordicstc", suffix=""
):  # input: int,int
    figure_dir = (
        output_root
        + "/"
        + "sub-"
        + str(sub).zfill(3)
        + "_ses-"
        + str(ses).zfill(2)
        + "_"
        + data_type
        + "_"
        + nordictype
        + "_"
        + suffix
        + "/figures"
    )
    if not os.path.exists(figure_dir):
        os.makedirs(figure_dir)
    return figure_dir


def apply_glmsingle_for_one_session(
    sub,
    ses,
    datatype="T1W",
    nordictype="nordicstc",
    suffix="",
    outputtype=[1, 1, 1, 1],
    shift=0,
    save_nifti=True,
):
    bolds = construct_bold_for_one_session(sub, ses, datatype, nordictype)
    designs = construct_design_for_one_session(sub, ses, shift)
    output_dir = construct_output_dir(sub, ses, datatype, nordictype, suffix)
    figuredir = construct_figuredir(sub, ses, datatype, nordictype, suffix)
    opt = dict()
    # set important fields for completeness (but these would be enabled by default)
    opt["wantlibrary"] = 1
    opt["wantglmdenoise"] = 1
    if outputtype[-1] == 1:
        opt["wantfracridge"] = 1
    else:
        opt["wantfracridge"] = 0
    # for the purpose of this example we will keep the relevant outputs in memory
    # and also save them to the disk
    opt["wantfileoutputs"] = outputtype
    opt["wantmemoryoutputs"] = outputtype

    # opt['n_pcs'] = 3###################################################
    # opt['brainthresh'] = [99, 0] # which allows all voxels to pass the intensity threshold --> we use surface data#####
    # opt['brainR2'] = 0.05

    # running python GLMsingle involves creating a GLM_single object
    # and then running the procedure using the .fit() routine
    # set modelmd as full set of single trial regressors
    glmsingle_obj = GLM_single(opt)
    glmsingle_obj.fit(
        design=designs,
        data=bolds,
        stimdur=2.5,
        tr=0.9,
        outputdir=output_dir,
        figuredir=figuredir,
    )
    # save the niftis
    if save_nifti:
        save_niftis_for_one_folder(output_dir, sub, ses)


if __name__ == "__main__":

    apply_glmsingle_for_one_session(
        sub=2,
        ses=8,
        datatype="T1W",
        nordictype="nordicstc",
        suffix="mainfull_endfix",
        shift=0,
    )

    apply_glmsingle_for_one_session(
        sub=2,
        ses=9,
        datatype="T1W",
        nordictype="nordicstc",
        suffix="mainfull_endfix",
        shift=0,
    )
