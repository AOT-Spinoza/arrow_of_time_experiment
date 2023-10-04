import sys
import os
import numpy as np
import cortex
import matplotlib.pyplot as plt
import pickle
import nibabel as nib

'''
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
'''

dataallfile = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_voxels/all/TYPED_FITHRF_GLMDENOISE_RR.npy'
data72file = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_voxels/72/TYPED_FITHRF_GLMDENOISE_RR.npy'
data90file = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_voxels/90/TYPED_FITHRF_GLMDENOISE_RR.npy'
data80file = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_voxels/80/TYPED_FITHRF_GLMDENOISE_RR.npy'
condition_order_list = pickle.load(open('/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/output/condition_order_list.pkl','rb'))
#condition order list for task all :72 80 90


task_list = ['72','90','80']
save_dir = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_voxels' 


dataall = np.load(dataallfile,allow_pickle=True).item()
data72 = np.load(data72file,allow_pickle=True).item()
data90 = np.load(data90file,allow_pickle=True).item()
data80 = np.load(data80file,allow_pickle=True).item()

betasall = dataall['betasmd']
betas72 = data72['betasmd']
betas90 = data90['betasmd']
betas80 = data80['betasmd']
print('betasall.shape:',betasall.shape)
print('betas72.shape:',betas72.shape)
print('betas90.shape:',betas90.shape)
print('betas80.shape:',betas80.shape)

#chekc nan
'''
if np.isnan(betasall).any():
    print('nan in betasall')
if np.isnan(betas72).any():
    print('nan in betas72')
if np.isnan(betas90).any():
    print('nan in betas90')
if np.isnan(betas80).any():
    print('nan in betas80')
'''

#count nan numbers

print('nan in betasall:',np.count_nonzero(np.isnan(betasall)))
print('nan in betas72:',np.count_nonzero(np.isnan(betas72)))
print('nan in betas90:',np.count_nonzero(np.isnan(betas90)))
print('nan in betas80:',np.count_nonzero(np.isnan(betas80)))


##print(betas72)





def get_repeat_condition_dict():
    condition_dict = {}
    for i in range(len(condition_order_list)):
        condition_dict[condition_order_list[i]] = []
    for i in range(len(condition_order_list)):
        condition_dict[condition_order_list[i]].append(i)
    return condition_dict

def get_repeat_6_condition_dict_taskall():
    old_condition_dict = get_repeat_condition_dict()
    condition_dict = {}
    #we only need these conditions that repeat 6 times
    for key in old_condition_dict.keys():
        if len(old_condition_dict[key]) == 6:
            condition_dict[key] = old_condition_dict[key]
    print(condition_dict)
    return condition_dict

def concatentate_betas_for_all_tasks(betas72,betas90,betas80):
    betas_concated = np.concatenate((betas72,betas90,betas80),axis=3)
    print('betas_concated.shape:',betas_concated.shape)
    return betas_concated

def compute_betas_dict_for_each_condition_task(betas_concated,condition_dict):
    beta_dict_72 = {}
    beta_dict_90 = {}
    beta_dict_80 = {}
    for key in condition_dict.keys():
        beta_dict_72[key] = []
        beta_dict_90[key] = []
        beta_dict_80[key] = []
        for index in condition_dict[key]:
            if index < 144:
                beta_dict_72[key].append(betas_concated[:,:,:,index])
            elif 144<= index <(144+180):
                beta_dict_90[key].append(betas_concated[:,:,:,index])
            elif (144+180)<= index <(144+180+160):
                beta_dict_80[key].append(betas_concated[:,:,:,index])
            else:
                print('index out of range:',index)
    return beta_dict_72,beta_dict_90,beta_dict_80

def compute_corrolation_for_each_condition_task(beta_dict_72,beta_dict_90,beta_dict_80):
    betameandiff_img_72 = pickle.load(open('/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_voxels/average_distance_map_72.pkl','rb'))
    betameandiff_img_90 = pickle.load(open('/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_voxels/average_distance_map_90.pkl','rb'))
    betameandiff_img_80 = pickle.load(open('/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_voxels/average_distance_map_80.pkl','rb'))
    R2_img_all = nib.load('/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/code/all_R2.nii.gz')
    betameandiff_data_72 = betameandiff_img_72#.get_fdata()
    betameandiff_data_90 = betameandiff_img_90#.get_fdata()
    betameandiff_data_80 = betameandiff_img_80#.get_fdata()
    R2_data_all = R2_img_all.get_fdata()
    print('betameandiff_data_72.shape:',betameandiff_data_72.shape)
    print('betameandiff_data_90.shape:',betameandiff_data_90.shape)
    print('betameandiff_data_80.shape:',betameandiff_data_80.shape)
    orig_image_fn = '/tank/shared/2022/arrow_of_time/preproc7/sub-001/ses-pilot/func/sub-001_ses-pilot_task-90_acq-nordic_run-01_space-T1w_desc-preproc_bold.nii.gz'
    bg_image_fn = '/tank/shared/2022/arrow_of_time/preproc7/sub-001/ses-pilot/func/sub-001_ses-pilot_task-90_acq-nordic_run-01_space-T1w_boldref.nii.gz'
    bm_image_fn = '/tank/shared/2022/arrow_of_time/preproc7/sub-001/ses-pilot/func/sub-001_ses-pilot_task-90_acq-nordic_run-01_space-T1w_desc-brain_mask.nii.gz'
    r2mask = R2_data_all > 25
    bmask = nib.load(bm_image_fn).get_fdata().astype(bool)
    bmask = np.logical_and(bmask, r2mask)
    def mask(data,bmask = bmask):
        maskeddata = np.zeros_like(data)
        maskeddata[bmask] = data[bmask]
        return maskeddata
    def compute_corrolation_for_one_task(beta_dict):
        corrolation_dict = {}
        for key in beta_dict.keys():
            corrolation_dict[key] = []
            '''
            for i in range(len(beta_dict[key])):
                for j in range(i+1,len(beta_dict[key])):
                    #data_combine = np.concatenate((beta_dict[key][i].flatten(),beta_dict[key][j].flatten()),axis=0) 
                    corr_matrix = np.corrcoef(beta_dict[key][i].flatten(),beta_dict[key][j].flatten())
                    print('corr_matrix.shape:',corr_matrix.shape)
                    corrolation_dict[key].append(corr_matrix[0,1])
                    #print('corrolation_dict[key].shape:',corrolation_dict[key].shape)
                    #print('corrolation_dict[key]:',corrolation_dict[key])
            '''
            x = mask(beta_dict[key][0])
            y = mask(beta_dict[key][1])
            print("shape x:",x.shape)
            print('nan in x:',np.count_nonzero(np.isnan(x)))
            print("shape y:",y.shape)
            print('nan in y:',np.count_nonzero(np.isnan(y)))
            #x = beta_dict[key][0].flatten()
            #y = beta_dict[key][1].flatten()
            x = x.flatten()
            y = y.flatten()
            print("shape x:",x.shape)
            print('nan in x:',np.count_nonzero(np.isnan(x)))
            print("shape y:",y.shape)
            print('nan in y:',np.count_nonzero(np.isnan(y)))
            #remove nan

            x = x[~np.isnan(x)]
            y = y[~np.isnan(y)]
            
            print("shape x nan removed:",x.shape)
            print("shape y nan removed:",y.shape)
            if x.shape == y.shape:
                corr_matrix = np.corrcoef(x,y)
                corr = corr_matrix[0,1]
                print('corr:',corr)
                corrolation_dict[key] = corr
            else:
                print('x and y shape not equal')
            
            #print('corrolation_dict[key].shape:',corrolation_dict[key].shape)
            #print('corrolation_dict[key]:',corrolation_dict[key])           
        return corrolation_dict
    corrolation_dict_72 = compute_corrolation_for_one_task(beta_dict_72)
    corrolation_dict_90 = compute_corrolation_for_one_task(beta_dict_90)
    corrolation_dict_80 = compute_corrolation_for_one_task(beta_dict_80)
    pickle.dump(corrolation_dict_72,open(os.path.join(save_dir,'corrolation_dict_72.pkl'),'wb'))
    pickle.dump(corrolation_dict_90,open(os.path.join(save_dir,'corrolation_dict_90.pkl'),'wb'))
    pickle.dump(corrolation_dict_80,open(os.path.join(save_dir,'corrolation_dict_80.pkl'),'wb'))
    return corrolation_dict_72,corrolation_dict_90,corrolation_dict_80


def compute_mean_beta_for_each_condition_task(betas_concated,betas_all,condition_dict):#betas_all is the betas for all tasks, beta_concated is the betas for 72,90,80 (they are different!)
    beta_dict_72 = {}
    beta_dict_90 = {}
    beta_dict_80 = {}
    beta_dict_all = {}
    mean_beta_dict_72 = {}
    mean_beta_dict_90 = {}
    mean_beta_dict_80 = {}
    mean_beta_dict_all = {}
    for key in condition_dict.keys():
        beta_dict_72[key] = []
        beta_dict_90[key] = []
        beta_dict_80[key] = []
        beta_dict_all[key] = []
        for index in condition_dict[key]:
            beta_dict_all[key].append(betas_all[:,:,:,index])
            if index < 144:
                beta_dict_72[key].append(betas_concated[:,:,:,index])
            elif 144<= index <(144+180):
                beta_dict_90[key].append(betas_concated[:,:,:,index])
            elif (144+180)<= index <(144+180+160):
                beta_dict_80[key].append(betas_concated[:,:,:,index])
            else:
                print('index out of range:',index)

        mean_beta_dict_72[key] = np.mean(np.array(beta_dict_72[key]),axis=0)
        mean_beta_dict_90[key] = np.mean(np.array(beta_dict_90[key]),axis=0)
        mean_beta_dict_80[key] = np.mean(np.array(beta_dict_80[key]),axis=0)
        mean_beta_dict_all[key] = np.mean(np.array(beta_dict_all[key]),axis=0)
    return mean_beta_dict_72,mean_beta_dict_90,mean_beta_dict_80,mean_beta_dict_all


def compare_mean_betas(mean_beta_dict_72,mean_beta_dict_90,mean_beta_dict_80,mean_beta_dict_all):
    compare_dict_72 = {}
    compare_dict_90 = {}
    compare_dict_80 = {}
    for key in mean_beta_dict_all.keys():
        #print(key,mean_beta_dict_all[key].shape)########################################
        #check nan
        if np.isnan(mean_beta_dict_all[key]).any():
            print('nan in mean_beta_dict_all:',key)
        compare_dict_72[key] = np.abs(mean_beta_dict_72[key]-mean_beta_dict_all[key])
        #print('compare_dict_72:',key,compare_dict_72[key])#############################################
        #contains nan or not
        if np.isnan(compare_dict_72[key]).any():
            print('nan in compare_dict_72:',key)
        compare_dict_90[key] = np.abs(mean_beta_dict_90[key]-mean_beta_dict_all[key])
        compare_dict_80[key] = np.abs(mean_beta_dict_80[key]-mean_beta_dict_all[key])

    print('compare_dict_72 keys:',compare_dict_72.keys())
    print('compare_dict_90 keys:',compare_dict_90.keys())
    print('compare_dict_80 keys:',compare_dict_80.keys())
    #save the compare_dict
    pickle.dump(compare_dict_72,open(os.path.join(save_dir,'compare_dict_72.pkl'),'wb'))
    pickle.dump(compare_dict_90,open(os.path.join(save_dir,'compare_dict_90.pkl'),'wb'))
    pickle.dump(compare_dict_80,open(os.path.join(save_dir,'compare_dict_80.pkl'),'wb'))

    return compare_dict_72,compare_dict_90,compare_dict_80

def final_compare_maps_average_condition(compare_dict_72,compare_dict_90,compare_dict_80):
    def condition_average_distance_for_one_task(compare_dict):
        maplist = []
        for key in compare_dict.keys():
            maplist.append(compare_dict[key])
        maplist = np.array(maplist)
        map = np.mean(maplist,axis=0)
        return map
    average_distance_map_72 = condition_average_distance_for_one_task(compare_dict_72)
    average_distance_map_90 = condition_average_distance_for_one_task(compare_dict_90)
    average_distance_map_80 = condition_average_distance_for_one_task(compare_dict_80)
    print('average_distance_map_72:',average_distance_map_72.shape)
    print('average_distance_map_90:',average_distance_map_90.shape)
    print('average_distance_map_80:',average_distance_map_80.shape)
    #count nan numbers
    print('nan in average_distance_map_72:',np.count_nonzero(np.isnan(average_distance_map_72)))
    print('nan in average_distance_map_90:',np.count_nonzero(np.isnan(average_distance_map_90)))
    print('nan in average_distance_map_80:',np.count_nonzero(np.isnan(average_distance_map_80)))

    #save the average_distance_map 
    pickle.dump(average_distance_map_72,open(os.path.join(save_dir,'average_distance_map_72.pkl'),'wb'))
    pickle.dump(average_distance_map_90,open(os.path.join(save_dir,'average_distance_map_90.pkl'),'wb'))
    pickle.dump(average_distance_map_80,open(os.path.join(save_dir,'average_distance_map_80.pkl'),'wb'))

    return average_distance_map_72,average_distance_map_90,average_distance_map_80 



    
    
        
        
if __name__ == '__main__':
    condition_dict = get_repeat_6_condition_dict_taskall()
    betas_concated = concatentate_betas_for_all_tasks(betas72,betas90,betas80)
    #mean_beta_dict_72,mean_beta_dict_90,mean_beta_dict_80,mean_beta_dict_all = compute_mean_beta_for_each_condition_task(betas_concated,betasall,condition_dict)
    #compare_dict_72,compare_dict_90,compare_dict_80 = compare_mean_betas(mean_beta_dict_72,mean_beta_dict_90,mean_beta_dict_80,mean_beta_dict_all)
    #final_compare_maps_average_condition(compare_dict_72,compare_dict_90,compare_dict_80)
    beta_dict_72,beta_dict_90,beta_dict_80 = compute_betas_dict_for_each_condition_task(betas_concated,condition_dict)
    #get correlation for each condition
    corrolation_dict_72,corrolation_dict_90,corrolation_dict_80 = compute_corrolation_for_each_condition_task(beta_dict_72,beta_dict_90,beta_dict_80)
    #average_distance_map_72,average_distance_map_90,average_distance_map_80 = condition_average_distance_for_tasks(compare_dict_72,compare_dict_90,compare_dict_80)
    pass

    #for key in mean_beta_dict_72.keys():
    #    print(key,mean_beta_dict_72[key].shape)
    #    print(mean_beta_dict_72[key])
    #for key in mean_beta_dict_90.keys():
    #    print(key,mean_beta_dict_90[key].shape)
    #for key in mean_beta_dict_80.keys():
    #    print(key,mean_beta_dict_80[key].shape)
    #for key in mean_beta_dict_all.keys():
    #    print(key,mean_beta_dict_all[key].shape)

    #for key in mean_beta_dict_72.keys():
    #    print(key,mean_beta_dict_72[key].shape)
    #    plt.plot(mean_beta_dict_72[key])
    #    plt.show()
    #for key in mean_beta_dict_90.keys():
    #    print(key,mean_beta_dict_90[key].shape)
    #    plt.plot(mean_beta_dict_90[key])
    #    plt.show()
    #for key in mean_beta_dict_80.keys():
    #    print(key,mean_beta_dict_80[key].shape)
    #    plt.plot(mean_beta_dict_80[key])
    #    plt.show()
    #for key in mean_beta_dict_all.keys():
    #    print(key,mean_beta_dict_all[key].shape)
    #    plt.plot(mean_beta_dict_all[key])
    #    plt.show()

    #for key in mean_beta_dict_72.keys():
    #    print(key,mean_beta_dict_72[key].shape)
    #    plt.plot(mean_beta_dict_72[key])
    #    plt.show()
    #for key in mean_beta_dict_90.keys():
    #    print(key,mean_beta_dict_90[key].shape)
    #    plt.plot(mean_beta_dict_90[key])
    #    plt.show()
    #for key in mean_beta





