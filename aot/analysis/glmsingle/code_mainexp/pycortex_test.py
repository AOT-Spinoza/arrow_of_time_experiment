import os, sys
import cortex
import nibabel as nib
import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as pl
import time


data_dir = '/tank/shared/2022/arrow_of_time/arrow_of_time_exp/aot/analysis/glmsingle/outputs/mainexp'
fs_dir = '/tank/shared/2022/arrow_of_time/derivatives/fmripreps/aotfull_preprocs/fullpreproc03/sourcedata/freesurfer'
os.listdir("/tank/zhangs/anaconda3/share/pycortex/db")

os.system("ln -s '/tank/shared/2022/arrow_of_time/derivatives/fmripreps/aotfull_preprocs/fullpreproc03/sourcedata/freesurfer/sub-001/surf/lh.pial.T1' '/tank/shared/2022/arrow_of_time/derivatives/fmripreps/aotfull_preprocs/fullpreproc03/sourcedata/freesurfer/sub-001/surf/lh.pial'")
os.system("ln -s '/tank/shared/2022/arrow_of_time/derivatives/fmripreps/aotfull_preprocs/fullpreproc03/sourcedata/freesurfer/sub-001/surf/rh.pial.T1' '/tank/shared/2022/arrow_of_time/derivatives/fmripreps/aotfull_preprocs/fullpreproc03/sourcedata/freesurfer/sub-001/surf/rh.pial'")

for i in [1]:
    cortex.freesurfer.import_subj(fs_subject='sub-'+str(i).zfill(3), cx_subject='sub-'+str(i).zfill(3), freesurfer_subject_dir=fs_dir)
    #cortex.freesurfer.import_flat('sub-'+str(i).zfill(3), patch='full', freesurfer_subject_dir=fs_dir)


test_data_path = '/tank/shared/2022/arrow_of_time/arrow_of_time_exp/aot/analysis/glmsingle/outputs/mainexp/sub-001_ses-01_voxel/TYPEC_FITHRF_GLMDENOISE.npy'
test_data = np.load(test_data_path, allow_pickle=True).item()
#print(test_data)
#os.system("ln -s '/tank/shared/2022/arrow_of_time/derivatives/fmripreps/aotfull_preprocs/fullpreproc03/sourcedata/freesurfer/sub-001/surf/lh.pial.T1' '/tank/shared/2022/arrow_of_time/derivatives/fmripreps/aotfull_preprocs/fullpreproc03/sourcedata/freesurfer/sub-001/surf/lh.pial'")

for key in test_data:
    print(key)
#R2 = test_data['onoffR2']
R2 = test_data['R2']
##meanvol = test_data['meanvol']
#noisepool = test_data['noisepool']
#HRFindex = test_data['HRFindex']
#fracvalue = test_data['FRACvalue']
# print(test_data['meanvol'])
#print(test_data['noisepool'].shape)
#print(test_data['R2'].shape)
#print(noisepool)

betas = test_data['betasmd']
print(betas.shape)
# #switch the first and second dimension
# betas = np.swapaxes(betas,0,1)

#betamean = np.mean(betas,axis=3)
#print(betamean.shape)

orig_image_fn = '/tank/shared/2022/arrow_of_time/derivatives/fmripreps/aotfull_preprocs/fullpreproc03/sub-001/ses-01/func/sub-001_ses-01_task-AOT_run-1_space-T1w_desc-preproc_bold.nii.gz'
bg_image_fn = '/tank/shared/2022/arrow_of_time/derivatives/fmripreps/aotfull_preprocs/fullpreproc03/sub-001/ses-01/func/sub-001_ses-01_task-AOT_run-1_space-T1w_boldref.nii.gz'
bm_image_fn = '/tank/shared/2022/arrow_of_time/derivatives/fmripreps/aotfull_preprocs/fullpreproc03/sub-001/ses-01/func/sub-001_ses-01_task-AOT_run-1_space-T1w_desc-brain_mask.nii.gz'

bmask = nib.load(bm_image_fn).get_fdata().astype(bool)
R2_masked = np.zeros_like(R2)
R2_masked[bmask] = R2[bmask]
#betamean_masked = np.zeros_like(betamean)
#betamean_masked[bmask] = betamean[bmask]


orig_image = nib.load(orig_image_fn)
#R2_img = nib.Nifti1Image(R2_masked, affine=orig_image.affine, header=orig_image.header)
#betamean_img = nib.Nifti1Image(betamean_masked, affine=orig_image.affine, header=orig_image.header)

#create a cortex volume
R2_cortex = cortex.Volume(R2_masked, 'sub-001', 'ses-01', 'R2', cmap='BuBkRd', vmin=15, vmax=60)
#create a dataset
R2_ds = cortex.Dataset(R2=R2_cortex)





web_view = True

handle = cortex.webgl.show(data=R2_ds, recache=False, port=12001)





