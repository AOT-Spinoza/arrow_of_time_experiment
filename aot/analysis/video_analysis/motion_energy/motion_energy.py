import moten
import pickle

# Stream and convert the RGB video into a sequence of luminance images
# video_file = '/Users/shufanzhang/Documents/PhD/Arrow_of_time/arrow_of_time_spinoza/stimuli_flat/R_S_-CyI3hUfiOY_23.mp4'
video_file = (
    "/tank/shared/2022/arrow_of_time/arrow_of_time4/videos1/R_S__6qAy77ODUI_175.mp4"
)
luminance_images = moten.io.video2luminance(video_file)

# Create a pyramid of spatio-temporal gabor filters
nimages, vdim, hdim = luminance_images.shape
print(nimages, vdim, hdim)
pyramid = moten.get_default_pyramid(vhsize=(vdim, hdim), fps=24)

# Compute motion energy features
moten_features = pyramid.project_stimulus(luminance_images)
print(moten_features)
print(moten_features.shape)

# Save the features
with open("moten_features.pkl", "wb") as f:
    pickle.dump(moten_features, f)
