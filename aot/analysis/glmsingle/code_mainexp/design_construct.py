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

# bold_data_root = '/tank/shared/2022/arrow_of_time/aotfull_preprocs/fullpreproc3/sub-001/ses-01/func'
# bold_data_root_wrong = '/tank/shared/2022/arrow_of_time/aotfull_preprocs/fullpreproc03/sub-001/ses-01/func'
bold_data_root = "/tank/shared/2022/arrow_of_time/derivatives/fmripreps/aotfull_preprocs/fullpreprocFinal"
output_root = "/tank/shared/2022/arrow_of_time/arrow_of_time_exp/aot/analysis/glmsingle/outputs/mainexp"
design_output_root = '/tank/shared/2022/arrow_of_time/arrow_of_time_exp/aot/analysis/glmsingle/outputs/design'


def movie_conditions_dict():  # include blank condition as 0
    original_video_names = []
    for i in range(1, len(video_db)):
        if (
            video_db["grade"][i] != "k" and video_db["grade"][i] != "l"
        ):  # video_db['grade'][i] == 'j' or video_db['grade'][i] == 'NA':
            original_video_names.append(video_db["video_name"][i])
    print("original videos number: ", len(original_video_names))
    resampled_video_names = [
        "S_" + name for name in original_video_names
    ]  # for gradin and labeling
    reversed_video_names = ["R_" + name for name in resampled_video_names]
    total_video_names = copy.deepcopy(resampled_video_names) + copy.deepcopy(
        reversed_video_names
    )
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


def construct_design_from_exp_design_yml(ymlfile, movies_conditions):
    BLANK = -1
    # read in the experiment design yaml file
    settings_sample = yaml.load(open(ymlfile), Loader=yaml.FullLoader)
    # get the movie files
    movies = settings_sample["stimuli"]["movie_files"]
    original_condition_list = [movies_conditions[movie] for movie in movies]
    # add blank condition to each element in the list
    # original_condition_list = [[x,x]+[0,0] for x in original_condition_list]
    original_condition_list = [
        [x] + [BLANK, BLANK, BLANK] for x in original_condition_list
    ]
    # flatten the list
    original_condition_list = [
        item for sublist in original_condition_list for item in sublist
    ]
    # add 16 0s to the start and end of the list
    original_condition_list = [BLANK] * 16 + original_condition_list + [BLANK] * 16
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
    target_path =  design_output_root +"/"+ f"design_sub_{sub}_ses_{ses}_run_{run}.npy"
    return target_path


def construct_design_for_one_session(sub, ses):
    list_of_designs = []
    for run in range(1, run_number + 1):
        # if run == 2:###################################
        #    continue
        target_path = index_to_exp_yml(sub, ses, run)
        newdesign = construct_design_from_exp_design_yml(target_path, movie_conditions)
        save_path = index_to_design_output(sub, ses, run)
        np.save(save_path, newdesign)
        list_of_designs.append(
            newdesign
        )
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
    # print('bold data:',img_L)
    img_data_L = [x.data for x in img_L.darrays]
    # print('bold data:',img_data_L)
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


def index_to_bold_data_T1W(sub, ses, run):  # input: int,int,int
    # sample : /tank/shared/2022/arrow_of_time/aotfull_preprocs/fullpreproc3/sub-001/ses-01/func/sub-001_ses-01_task-AOT_run-1_space-T1w_desc-preproc_bold.nii.gz
    sub = str(sub)
    ses = str(ses)
    run = str(run)
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
        + "_task-AOT_run-"
        + run
        + "_space-T1w_desc-preproc_bold.nii.gz"
    )
    img = nib.load(bold_path)
    img_data = img.get_fdata()
    print("bold data shape:", img_data.shape)
    return img_data


def construct_bold_for_one_session(sub, ses, datatype):  # fsnative or §T1W
    list_of_bold_data = []
    if datatype == "fsaverage":
        for run in range(1, run_number + 1):
            # if run == 2:###################################
            #    continue
            list_of_bold_data.append(index_to_bold_data_fsaverage(sub, ses, run))
        return list_of_bold_data
    elif datatype == "T1W":
        for run in range(1, run_number + 1):
            # if run == 2:###################################
            #    continue
            list_of_bold_data.append(index_to_bold_data_T1W(sub, ses, run))
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


def construct_output_dir(sub, ses, data_type="T1W", suffix=""):  # input: int,int
    output_dir = (
        output_root
        + "/"
        + "sub-"
        + str(sub).zfill(3)
        + "_ses-"
        + str(ses).zfill(2)
        + "_"
        + data_type
        + "_merge_"
        + suffix
    )
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def apply_glmsingle_for_one_session(sub, ses, datatype="T1W", suffix=""):
    bolds = construct_bold_for_one_session(sub, ses, datatype)
    designs = construct_design_for_one_session(sub, ses)
    output_dir = construct_output_dir(sub, ses, datatype, suffix)
    opt = dict()
    # set important fields for completeness (but these would be enabled by default)
    opt["wantlibrary"] = 1
    opt["wantglmdenoise"] = 1
    opt["wantfracridge"] = 1
    # for the purpose of this example we will keep the relevant outputs in memory
    # and also save them to the disk
    opt["wantfileoutputs"] = [1, 1, 1, 1]
    opt["wantmemoryoutputs"] = [1, 1, 1, 1]

    # opt['n_pcs'] = 3###################################################
    # opt['brainthresh'] = [99, 0] # which allows all voxels to pass the intensity threshold --> we use surface data#####
    # opt['brainR2'] = 0.05

    # running python GLMsingle involves creating a GLM_single object
    # and then running the procedure using the .fit() routine
    # set modelmd as full set of single trial regressors
    glmsingle_obj = GLM_single(opt)
    glmsingle_obj.fit(
        design=designs, data=bolds, stimdur=2.5, tr=0.9, outputdir=output_dir
    )


if __name__ == "__main__":
    #movie_conditions = movie_conditions_dict()
    # sample_yml = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/data/experiment/settings/main/experiment_settings_sub_01_ses_01_run_01.yml'
    # construct_design_from_exp_design_yml(sample_yml, movie_conditions)
    # sample_bold = index_to_bold_data_T1W(1,1,1)

    #design_list = construct_design_for_one_session(sub=2,ses=1)
    # print(len(design_list))
    # bold_list = construct_bold_for_one_session(sub=1,ses=1,datatype='T1W')
    # print(len(bold_list))

    apply_glmsingle_for_one_session(sub=2, ses=1, datatype="T1W", suffix="glmnew_runfix")
    apply_glmsingle_for_one_session(sub=1,ses=1, datatype='T1W',suffix='glmnew_runfix')
