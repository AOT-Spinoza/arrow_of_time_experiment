import sys
import os
import numpy as np
import cortex
import matplotlib.pyplot as plt
import pickle
from nilearn.plotting import view_img
import nibabel as nib
import subprocess as sp
import shlex


#test_data_path = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_voxels/72/TYPEA_ONOFF.npy'
#test_data_path = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_voxels/72/TYPEB_FITHRF.npy'
#test_data_path = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_voxels/72/TYPEC_FITHRF_GLMDENOISE.npy'
test_data_path = '/tank/shared/2022/arrow_of_time/arrow_of_time/aot/analysis/glmsingle/outputon7_voxels/72/TYPED_FITHRF_GLMDENOISE_RR.npy'
fs_dir = '/tank/shared/2022/arrow_of_time/preproc7/sourcedata/freesurfer'

test_data = np.load(test_data_path, allow_pickle=True).item()
#print(test_data)


for key in test_data:
    print(key)
#onoffR2 = test_data['onoffR2']
R2 = test_data['R2']
meanvol = test_data['meanvol']
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

betamean = np.mean(betas,axis=3)
print(betamean.shape)

orig_image_fn = '/tank/shared/2022/arrow_of_time/preproc7/sub-001/ses-pilot/func/sub-001_ses-pilot_task-72_acq-nordic_run-01_space-T1w_desc-preproc_bold.nii.gz'
bg_image_fn = '/tank/shared/2022/arrow_of_time/preproc7/sub-001/ses-pilot/func/sub-001_ses-pilot_task-72_acq-nordic_run-01_space-T1w_boldref.nii.gz'
bm_image_fn = '/tank/shared/2022/arrow_of_time/preproc7/sub-001/ses-pilot/func/sub-001_ses-pilot_task-72_acq-nordic_run-01_space-T1w_desc-brain_mask.nii.gz'

bmask = nib.load(bm_image_fn).get_fdata().astype(bool)
R2_masked = np.zeros_like(R2)
R2_masked[bmask] = R2[bmask]

orig_image = nib.load(orig_image_fn)
R2_img = nib.Nifti1Image(R2_masked, affine=orig_image.affine, header=orig_image.header)

#view_img(R2_img, threshold=15, vmax=50, cmap='hot', symmetric_cmap=False, bg_img=bg_image_fn)
'''

#cmd = "ls"
#print(sp.check_output(shlex.split(cmd)))


print(os.system("mri_convert"))


'''
#cmd = "mri_convert"
#cmd = "ls"
#print(sp.check_output(shlex.split(cmd)))


subject = 'sub-001'

cortex.freesurfer.import_subj(subject, subject, fs_dir, 'smoothwm')