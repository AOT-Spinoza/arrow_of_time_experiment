# Arrow of time experiment

This experiment is based on exptools2.

## Display calibration

The 7T display is a 1920 × 1080 BOLDscreen 32, with an active width of
69.84 cm and a physical eye-to-screen optical path of **196 cm** via the mirror.
The current experiment templates use this calibration. Historical run settings
are acquisition records: do not rewrite their old calibration values or use
those values as measurements of physical viewing distance. Changing the current
monitor calibration can affect degree-based elements; validate fixation and
EyeLink calibration on the scanner before collecting another run.



Now the folder structure for videos is as follows:
    
    ``` 
    ├── stimulis
    │   ├──raws(categories)
    │   ├──resampled(stretched)
    │   ├──reversed
    │ 
    ├── stimulis_flat

    ```

before running the experiment, you need to 

1)pip install -e . in the root folder

2)edit stimuli_path in aot/experiment/core_exp_settings.yml for videos path


Note: the experiment and experiment is for both resampled and reversed videos, but the grading and labeling experiment is only for resampled videos.


