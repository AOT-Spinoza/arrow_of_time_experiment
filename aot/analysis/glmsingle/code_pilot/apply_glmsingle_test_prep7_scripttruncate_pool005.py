import numpy as np
import nibabel as nib
import os
import sys
import pandas as pd
import yaml
from pathlib import Path
from glmsingle.glmsingle import GLM_single
import pickle

#auto truncate(by glmsingle) data,apply on   old design matrix constrction


def index_to_bold_file(task,run): #string,string
    #test_bold_file_L = '/tank/shared/2022/arrow_of_time/preproc7/sub-001/ses-pilot/func/sub-001_ses-pilot_task-'+task+'_acq-nordic_run-'+run+'_hemi-L_space-fsaverage_bold.func.gii'
    #test_bold_file_R = '/tank/shared/2022/arrow_of_time/preproc7/sub-001/ses-pilot/func/sub-001_ses-pilot_task-'+task+'_acq-nordic_run-'+run+'_hemi-R_space-fsaverage_bold.func.gii'
    #test_bold_file = '/tank/shared/2022/arrow_of_time/postproc/truncate/sub-001/ses-pilot/func/sub-001_ses-pilot_task-'+task+'_acq-nordic_run-'+run+'_hemi-L_space-fsaverage_bold.func.gii'
    test_bold_file_L = '/tank/shared/2022/arrow_of_time/postproc7/truncate/sub-001/ses-pilot/func/sub-001_ses-pilot_task-'+task+'_acq-nordic_run-'+run+'_hemi-L_space-fsaverage_bold.func.gii'
    test_bold_file_R = '/tank/shared/2022/arrow_of_time/postproc7/truncate/sub-001/ses-pilot/func/sub-001_ses-pilot_task-'+task+'_acq-nordic_run-'+run+'_hemi-R_space-fsaverage_bold.func.gii'
    return test_bold_file_L,test_bold_file_R

def index_to_events_file(task,run):
    #template = '/tank/shared/2022/arrow_of_time/aotpilot_copy/sub-001/ses-pilot/func/sub-001_ses-pilot_task-72_run-01_events.tsv'
    events_file = '/tank/shared/2022/arrow_of_time/aotpilot_copy/sub-001/ses-pilot/func/sub-001_ses-pilot_task-'+task+'_run-'+run+'_events.tsv'
    return events_file

#load and concatenate the bold data from left and right hemispheres
def merge_bold_data(test_bold_file_L,test_bold_file_R):
    
    img_L = nib.load(test_bold_file_L)
    img_data_L = [x.data for x in img_L.darrays]
    cur_data_L = np.array(img_data_L)[0]
    #cur_data_L = cur_data_L[5:,:]   #first five
    #cur_data_L = cur_data_L[:-5,:] #last five
    #swap the first two dimensions
    cur_data_L = np.swapaxes(cur_data_L,0,1)
    print('bold data shape:',cur_data_L.shape)
    img_R = nib.load(test_bold_file_R)
    img_data_R = [x.data for x in img_R.darrays]
    cur_data_R = np.array(img_data_R)[0]
    #cur_data_R = cur_data_R[5:,:]  #first five
    #cur_data_R = cur_data_R[:-5,:]  #last five
    cur_data_R = np.swapaxes(cur_data_R,0,1)
    print('bold data shape:',cur_data_R.shape)
    cur_data = np.concatenate((cur_data_L,cur_data_R),axis=0)
    print('bold data shape:',cur_data.shape)
    return cur_data #[vertex,time]



label_index = {'onset':0,'duration':1,'event_type':2,'phase':3,'response':4,'nr_frames':5,'movie_index':6,'movie_duration':7,'movie_file':8,'blank':9,'onset_abs':10,'trial_nr':11}

def movies_conditions_dict():
    settings_sample_path = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/code/pilot_settings/movies.yml'
    settings_sample = yaml.load(open(settings_sample_path), Loader=yaml.FullLoader)
    movies  = settings_sample['stimuli']['movie_files']
    movies_conditions = {}
    condnum = 0
    movies_conditions["blank"] = condnum
    for i in range(len(movies)):
        if movies[i] not in movies_conditions and movies[i] != 'blank':
            condnum += 1
            movies_conditions[movies[i]] = condnum
    return movies_conditions

condition_dict = movies_conditions_dict()
len_conditions = len(condition_dict)
print(condition_dict)

def construct_design_for_one_run(eventfile):
    run_events = pd.read_csv(eventfile, delimiter='\t')
    run_events = run_events.values.tolist()
    run_design = []
    index_list = []

    last_trail_nr = -1
    for i in range(len(run_events)):
        repeat = False
        #print(run_events[i])
        new_trail_nr = run_events[i][label_index['trial_nr']]
        if run_events[i][label_index['event_type']] == 'pulse':
            if new_trail_nr == last_trail_nr:
                repeat = True
                last_trail_nr = new_trail_nr
            else:
                repeat = False
                last_trail_nr = new_trail_nr
            
            movie = run_events[i][label_index['movie_file']]
            if type(movie) == str:
                if movie.endswith('.mp4'):
                    movie = Path(movie)
                    #get the full name of the movie
                    movie = movie.name
                else:
                    movie = 'blank'
            else:
                movie = 'blank'
            #print(movie)
            if movie not in condition_dict:
                print('movie not in condition dict:', movie)
                movie = 'blank'

            if movie == 'blank':
                new_time_slice = [0] * len_conditions
                run_design.append(new_time_slice)
                index_list.append(0)
            else:
                if not repeat:
                    new_time_slice = [0] * len_conditions
                    new_time_slice[condition_dict[movie]] = 1
                    index_list.append(condition_dict[movie])
                elif repeat:
                    new_time_slice = [0] * len_conditions
                    index_list.append(0)
                run_design.append(new_time_slice)
    print("list design:",run_design)
    print("index list:",index_list)
    run_design = np.array(run_design)
    print(run_design.shape)
    return run_design,index_list

def construct_design_for_all_runs(task):
    design_all_runs = []
    index_list_all_runs = []
    for run in [1,2]:
        events_file = index_to_events_file(task,str(run).zfill(2))
        design_one_run,index_list_one_run = construct_design_for_one_run(events_file)
        design_all_runs.append(design_one_run)
        index_list_all_runs.append(index_list_one_run)
    return design_all_runs,index_list_all_runs

def construct_bold_data_for_all_runs(task):
    bold_data_all_runs = []
    for run in [1,2]:
        test_bold_file_L,test_bold_file_R = index_to_bold_file(task,str(run).zfill(2))
        bold_data_one_run = merge_bold_data(test_bold_file_L,test_bold_file_R)
        bold_data_all_runs.append(bold_data_one_run)
    return bold_data_all_runs

def construct_output_dir(task):
    output_dir_base = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_scriptruncate_pc3_poollimited005'
    output_dir = os.path.join(output_dir_base,task)
    return output_dir


def apply_glmsingle_for_all_tasks():
    task_list = ['72','90','80']
    for task in task_list:
        apply_glmsingle_for_one_task(task)

def condition_order_list_for_all():
    def index_list_for_all_tasks():
        task_list = ['72','90','80']
        index_list_all_tasks = []
        for task in task_list:
            design_all_runs,index_list_all_runs = construct_design_for_all_runs(task)
            index_list_all_tasks.append(index_list_all_runs)
        #flatten the list twice
        index_list_all_tasks = [item for sublist in index_list_all_tasks for item in sublist]
        index_list_all_tasks = [item for sublist in index_list_all_tasks for item in sublist]
        print('index_list_all_tasks:',len(index_list_all_tasks))
        #pickle.dump(index_list_all_tasks,open('index_list_all_tasks.pkl','wb'))
        return index_list_all_tasks
    index_list_all_tasks = index_list_for_all_tasks()
    condition_order_list = [c for c in index_list_all_tasks if c != 0]
    print('condition_order_list:',len(condition_order_list))
    pickle.dump(condition_order_list,open('condition_order_list.pkl','wb'))
    return condition_order_list




def apply_glmsingle_for_one_task(task):
    design_all_runs,index_list_all_runs = construct_design_for_all_runs(task)
    bold_data_all_runs = construct_bold_data_for_all_runs(task)
    output_dir = construct_output_dir(task)
    opt = dict()
    # set important fields for completeness (but these would be enabled by default)
    opt['wantlibrary'] = 1
    opt['wantglmdenoise'] = 1
    opt['wantfracridge'] = 1
    # for the purpose of this example we will keep the relevant outputs in memory
    # and also save them to the disk
    opt['wantfileoutputs'] = [1,1,1,1]
    opt['wantmemoryoutputs'] = [1,1,1,1]

    opt['n_pcs'] = 3###################################################
    opt['brainthresh'] = [99, 0] # which allows all voxels to pass the intensity threshold --> we use surface data#####
    opt['brainR2'] = 0.05

    # running python GLMsingle involves creating a GLM_single object
    # and then running the procedure using the .fit() routine
    #set modelmd as full set of single trial regressors
    glmsingle_obj = GLM_single(opt)
    glmsingle_obj.fit(design=design_all_runs,data=bold_data_all_runs,stimdur=2.5,tr=1.6,outputdir=output_dir) 

def apply_glmsingle_for_all_together():
    design_all_runs = []
    bold_data_all_runs = []
    for task in ['72','90','80']:
        design_all_runs.append(construct_design_for_all_runs(task)[0])
        bold_data_all_runs.append(construct_bold_data_for_all_runs(task))
    #flatten the list
    design_all_runs = [item for sublist in design_all_runs for item in sublist]
    bold_data_all_runs = [item for sublist in bold_data_all_runs for item in sublist]
    print('design_all_runs:',len(design_all_runs))
    print('bold_data_all_runs:',len(bold_data_all_runs))
    output_dir = construct_output_dir('all')
    opt = dict()
    opt['wantlibrary'] = 1
    opt['wantglmdenoise'] = 1
    opt['wantfracridge'] = 1
    opt['wantfileoutputs'] = [1,1,1,1]
    opt['wantmemoryoutputs'] = [1,1,1,1]

    opt['n_pcs'] = 3###################################################
    opt['brainthresh'] = [99, 0] # which allows all voxels to pass the intensity threshold --> we use surface data#####
    opt['brainR2'] = 0.05

    glmsingle_obj = GLM_single(opt)
    glmsingle_obj.fit(design=design_all_runs,data=bold_data_all_runs,stimdur=2.5,tr=1.6,outputdir=output_dir)

if __name__ == '__main__':
    apply_glmsingle_for_all_tasks()
    apply_glmsingle_for_all_together()
    #condition_order_list_for_all()
    pass
    


        




        










