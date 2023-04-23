import moten

# Stream and convert the RGB video into a sequence of luminance images
video_file = '/Users/shufanzhang/Documents/PhD/Arrow_of_time/arrow_of_time_spinoza/stimuli_flat/R_S_-CyI3hUfiOY_23.mp4'
luminance_images = moten.io.video2luminance(video_file, nimages=100)

# Create a pyramid of spatio-temporal gabor filters
nimages, vdim, hdim = luminance_images.shape
pyramid = moten.get_default_pyramid(vhsize=(vdim, hdim), fps=24)

# Compute motion energy features
moten_features = pyramid.project_stimulus(luminance_images)
