# for i in range(1,17):
# cortex.freesurfer.import_subj(subject=‘sub-’+str(i).zfill(3), sname=‘sub-‘+str(i).zfill(3), freesurfer_subject_dir=‘/Users/knapen/FS_SJID’)
# cortex.freesurfer.import_flat(‘sub-’+str(i).zfill(3), patch=‘full’, freesurfer_subject_dir=‘/Users/knapen/FS_SJID’)
# for s in sub-003 sub-005 sub-006 sub-012 sub-014 sub-016
# do
#     scp knapen@aeneas.psy.vu.nl:/home/raw_data/2016/visual/whole_brain_MB_pRF/data/FS_SJID/$s/surf/*full.flat.patch.3d /Users/knapen/FS_SJID/$s/surf/
# done
import os, sys
import cortex
import nibabel as nb
import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as pl
import time
# aeneas
data_dir = '/tank/shared/2022/arrow_of_time/arrow_of_time_exp/aot/analysis/glmsingle/outputs/mainexp'
fs_dir = '/tank/shared/2022/arrow_of_time/derivatives/fmripreps/aotfull_preprocs/fullpreproc03/sourcedata/freesurfer'
# laptop
#data_dir = ‘/Users/knapen/disks/ae_S/2017/visual/npRF_all/derivatives/pp/’
#fs_dir = '/Users/shufanzhang/Desktop/freesurfer'
# import data into pycortex
for subj_nr in [1,2]: # 1,3,5,6,12,14,15,16,17
    sub = 'sub-%s' % str(subj_nr).zfill(3)
    xfmname = 'fmriprep_fsT1'
    # cortex.freesurfer.import_subj(
    #     subject=sub, sname=sub, freesurfer_subject_dir=fs_dir)
    # cortex.freesurfer.import_flat(
    #     sub, patch='full', freesurfer_subject_dir=fs_dir)
    # reference files for surface mapping of epi
    dd = os.path.join(data_dir, sub, 'ses-1')
    epi = os.path.join(dd, 'reg', 'epi.nii.gz')
    epi_2_T1 = os.path.join(dd, 'reg', 'bbr.mat')
    T1 = os.path.join(fs_dir, sub, 'mri', 'T1.nii.gz')
    os.system('mri_convert %s %s'%(T1[:-7]+'.mgz', T1))
    # T1 = cortex.db.get_anat(subject=sub).get_filename()
    # epi_2_T1 = data_location + \
    #     '2016/visual/prf/all_final/sub-%s/reg/example_func2highres.mat’ % str(
    #         subj_nr).zfill(3)
    # epi = data_location + \
    #     '2016/visual/prf/all_final/sub-%s/reg/example_func.nii.gz’ % str(
    #         subj_nr).zfill(3)
    # T1 = data_location + \
    #     '2016/visual/prf/all_final/sub-%s/reg/highres.nii.gz’ % str(
    #         subj_nr).zfill(3)
    add_session_2_cortex(epi_2_T1, epi, T1, sub, xfmname, transpose=False)
static_imgs = False
web_view = True
# polar angle and prf mapping stat maps
for subj_nr in [3, 5, 6, 12, 14, 16]:
    sub = 'sub-%s' % str(subj_nr).zfill(3)
    xfmname = 'fmriprep_fsT1'
    dd = os.path.join(data_dir, sub, 'ses-1', 'deriv')
    realf = os.path.join(dd, 'polar_real_all.nii.gz')
    imagf = os.path.join(dd, 'polar_imag_all.nii.gz')
    srsqf = os.path.join(dd, 'all_rsq_s.nii.gz')
    try:
        os.makedirs(os.path.join(data_dir, sub, 'ses-1', 'figs','surf'))
    except:
        pass
    # # # reading in the psc file data
    # print('loading psc dataset')
    # vpsc = cortex.Volume(psc_file, "sub-%s" % str(subj_nr).zfill(3),
    #                      "all_final", cmap="BuBkRd", vmin=-0.5, vmax=0.5)
    # polar angle data
    print('loading complex dataset')
    reald, imagd = nb.load(realf).get_data(), nb.load(imagf).get_data()
    polcomp = reald + 1j * imagd
    angs = np.angle(polcomp)
    rsq = np.abs(polcomp)
    s = np.ones(angs.shape)
    v = np.ones(angs.shape)
    angs_n = (angs + np.pi) / (np.pi * 2.0)
    # make discrete angles for clarity
    angle_offset = 0.08
    angs_discrete = np.fmod(angle_offset + (np.floor(angs_n * 6) / 6.0), 1.0)
    # convert angles to colors, using correlations as weights
    hsv = np.zeros(list(angs.shape) + [3])
    hsv[..., 0] = angs_discrete # angs_discrete  # angs_n
    hsv[..., 1] = np.sqrt(rsq) #np.ones_like(rsq)  # np.sqrt(rsq)
    # np.nan_to_num(rsq ** -3) # np.ones_like(rsq)#n
    hsv[..., 2] = np.sqrt(rsq)# np.ones_like(rsq)
    alpha_mask = (rsq <= 0.2).T
    alpha = np.sqrt(rsq).T * 5
    alpha[alpha_mask] = 0
    alpha = np.ones(alpha.shape)
    rgb = colors.hsv_to_rgb(hsv)
    ###########################################################################################
    # Datasets
    ###########################################################################################
    # r-squared data
    print('loading rsq dataset')
    vsrsq = cortex.Volume(data=nb.load(srsqf).get_data().T, subject="sub-%s" % str(subj_nr).zfill(3), #a.transpose((2,1,0))
                          xfmname=xfmname, cmap="BuBkRd", vmin=-1, vmax=1, with_dropout=8)
                          # mask=yeo_7_dmn_filename)
    vrgba = cortex.VolumeRGB(
        red=rgb[..., 0].T,
        green=rgb[..., 1].T,
        blue=rgb[..., 2].T,
        subject="sub-%s" % str(subj_nr).zfill(3),
        # np.sqrt(rsq).T * 5, # np.ones(rsq.T.shape), # np.sqrt(rsq).T * 5, #
        alpha=alpha,
        xfmname=xfmname)
        # mask=yeo_7_dmn_filename)
    # rework the data
    # normalize
    # vpsc.data = (vpsc.data - (vpsc.data.mean(axis=0)
    #                           [np.newaxis, ...])) / (vpsc.data.std(axis=0)[np.newaxis, ...])
    # # weight with signed rsq
    # vpsc.data *= np.sqrt(np.abs(vsrsq.data[np.newaxis, ...]))
    # creating a re-usable dataset
    ds = cortex.Dataset(rsq_s=vsrsq, polar=vrgba)
    ds.save(os.path.join(data_dir, sub, 'ses-1', 'h5', 'cortex_pa-rsq.h5'))
    # print('created all volume datasets')
    # # static figures
    if web_view:
        print('creating web view')
        # webview for movies and comparisons
        for d, nm, depth in zip([vsrsq, vrgba], ['rsq', 'polar'], [0, 0]):
            ds = cortex.Dataset(**{nm:d})
            handle = cortex.webgl.show(data=ds, recache=False, port=12001)
            file_pattern = "{base}_{view}_{nm}.png"
            time.sleep(20.0)
            # projection parameters
            basic = dict(radius=300, depth=depth, specularity=0, unfold=0.5, contrast=0) # projection=['orthographic’],
            # different views available, more views can be added  and the
            # existing list can be removed
            views = dict(lateral=dict(altitude=90.5, azimuth=181, pivot=180),
                         medial=dict(altitude=90.5, azimuth=0, pivot=180),
                         front=dict(altitude=90.5, azimuth=0, pivot=0),
                         back=dict(altitude=90.5, azimuth=181, pivot=0),
                         top=dict(altitude=0, azimuth=180, pivot=0),
                         bottom=dict(altitude=180, azimuth=0, pivot=0)
                        )
            # utility functions to set the different views
            prefix = dict(altitude='camera.', azimuth='camera.',
                          pivot='surface.{subject}.', radius='camera.',
                          unfold='surface.{subject}.', depth='surface.{subject}.',
                          specularity='surface.{subject}.', contrast='surface.curvature.')
            _tolists = lambda p: {prefix[k]+k:[v] for k,v in p.items()}
            _combine = lambda a,b: ( lambda c: [c, c.update(b)][0] )(dict(a))
            # Save images by iterating over the different views and surfaces
            for view,vparams in views.items():
                # Combine basic, view, and surface parameters
                params = _combine(basic, vparams)
                # Set the view
                handle._set_view(**_tolists(params))
                # Save image
                filename = file_pattern.format(base=sub, view=view, nm=nm)
                output_path = os.path.join(data_dir, sub, 'ses-1', 'figs','surf', filename)
                handle.getImage(output_path, size =(3840, 2160))
                # the block below trims the edges of the image:
                # wait for image to be written
                while not os.path.exists(output_path):
                    pass
                time.sleep(1.5)
                # try:
                #     import subprocess
                #     subprocess.call(["convert", "-trim", output_path, output_path])
                # except:
                #     pass
            # Close the window!
            handle.close()