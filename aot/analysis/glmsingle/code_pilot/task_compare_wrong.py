import sys
import os
import numpy as np
import cortex
import matplotlib.pyplot as plt
import pickle

fmridatafile = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_first5/all/TYPEC_FITHRF_GLMDENOISE.npy'
condition_order_list = pickle.load(open('/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/output/condition_order_list.pkl','rb'))
task_list = ['72','90','80']
save_dir = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_first5'


fmridata = np.load(fmridatafile,allow_pickle=True).item()
betas = fmridata['betasmd']
print('betas.shape:',betas.shape)
print(betas[:,0])

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

def compute_mean_beta_for_each_condition_taskall(betas,condition_dict):
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
            beta_dict_all[key].append(betas[:,index])
            if index < 144:
                beta_dict_72[key].append(betas[:,index])
            elif 144<= index <(144+180):
                beta_dict_90[key].append(betas[:,index])
            elif (144+180)<= index <(144+180+160):
                beta_dict_80[key].append(betas[:,index])
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
        print(key,mean_beta_dict_all[key].shape)
        compare_dict_72[key] = np.abs(mean_beta_dict_72[key]-mean_beta_dict_all[key])
        compare_dict_90[key] = np.abs(mean_beta_dict_90[key]-mean_beta_dict_all[key])
        compare_dict_80[key] = np.abs(mean_beta_dict_80[key]-mean_beta_dict_all[key])
        #add another dimension to make it compatible with mean
        #compare_dict_72[key] = np.expand_dims(compare_dict_72[key],axis=1)
        #compare_dict_90[key] = np.expand_dims(compare_dict_90[key],axis=1)
        #compare_dict_80[key] = np.expand_dims(compare_dict_80[key],axis=1)
        #transform to list
        #compare_dict_72[key] = compare_dict_72[key].tolist()
        #compare_dict_90[key] = compare_dict_90[key].tolist()
        #compare_dict_80[key] = compare_dict_80[key].tolist()
        #compare_dict_72[key] = np.mean(compare_dict_72[key],axis=0)
        #compare_dict_90[key] = np.mean(compare_dict_90[key],axis=0)
        #compare_dict_80[key] = np.mean(compare_dict_80[key],axis=0)
        #print(compare_dict_72[key])

        #get the mean of the absolute difference
        #compare_dict_72[key] = sum(compare_dict_72[key])/len(compare_dict_72[key])
        #compare_dict_90[key] = sum(compare_dict_90[key])/len(compare_dict_90[key])
        #compare_dict_80[key] = sum(compare_dict_80[key])/len(compare_dict_80[key])

    print('compare_dict_72:',compare_dict_72)
    print('compare_dict_90:',compare_dict_90)
    print('compare_dict_80:',compare_dict_80)
    #save the compare_dict
    pickle.dump(compare_dict_72,open(os.path.join(save_dir,'compare_dict_72.pkl'),'wb'))
    pickle.dump(compare_dict_90,open(os.path.join(save_dir,'compare_dict_90.pkl'),'wb'))
    pickle.dump(compare_dict_80,open(os.path.join(save_dir,'compare_dict_80.pkl'),'wb'))



    return compare_dict_72,compare_dict_90,compare_dict_80

def condition_average_distance_for_tasks(compare_dict_72,compare_dict_90,compare_dict_80):
    #average_distance_map_72
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
    #save the average_distance_map
    pickle.dump(average_distance_map_72,open(os.path.join(save_dir,'average_distance_map_72.pkl'),'wb'))
    pickle.dump(average_distance_map_90,open(os.path.join(save_dir,'average_distance_map_90.pkl'),'wb'))
    pickle.dump(average_distance_map_80,open(os.path.join(save_dir,'average_distance_map_80.pkl'),'wb'))

    return average_distance_map_72,average_distance_map_90,average_distance_map_80


    
    
        
        
if __name__ == '__main__':
    
    condition_dict = get_repeat_6_condition_dict()
    mean_beta_dict_72,mean_beta_dict_90,mean_beta_dict_80,mean_beta_dict_all = compute_mean_beta_for_each_condition(betas,condition_dict)
    #print('mean_beta_dict_72.keys():',mean_beta_dict_72.keys())
    #print('mean_beta_dict_90.keys():',mean_beta_dict_90.keys())
    #print('mean_beta_dict_80.keys():',mean_beta_dict_80.keys())
    #print('mean_beta_dict_all.keys():',mean_beta_dict_all.keys())
    
    compare_dict_72,compare_dict_90,compare_dict_80 = compare_mean_betas(mean_beta_dict_72,mean_beta_dict_90,mean_beta_dict_80,mean_beta_dict_all)
    average_distance_map_72,average_distance_map_90,average_distance_map_80 = condition_average_distance_for_tasks(compare_dict_72,compare_dict_90,compare_dict_80)
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





