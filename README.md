# Arrow of time experiment

This experiment is based on exptools2. 


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

1)edit rootpath in base_settings.yaml for code and output

2)edit rootpath_video in base_settings.yaml for videos and experiment settings

3)run the arrow_of_time/experiment/settings_code/all_experiments_yaml_gen.py to generate the yaml files for all the experiments.


Note: the experiment and labeling experiment is for both resampled and reversed videos, but the grading experiment is only for resampled videos.