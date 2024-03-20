import cortex
from cortex import fmriprep
from os import path as op

# Location of the downloaded openfmri dataset
source_directory = '/derivatives/ds000164'
# fmriprep subject name (without "sub-")
subject_id = '001'

# import subject into pycortex database
fmriprep.import_subj(subject_id, source_directory)

# We can visualize the imported subject's T1-weighted image
anat_nifti = 'fmriprep/sub-001/anat/sub-001_T1w_preproc.nii.gz'
t1_image_path = op.join(source_directory, anat_nifti)

# Now we can make a volume using the built-in identity transform
t1w_volume = cortex.Volume(t1_image_path, subject_id, 'identity')

# And show the result.
ds = cortex.Dataset(t1w=t1w_volume)
cortex.webgl.show(ds)