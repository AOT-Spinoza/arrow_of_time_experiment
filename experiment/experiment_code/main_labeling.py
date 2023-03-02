import os.path as op
import os
import argparse
import numpy as np
import scipy.stats as ss
import pandas as pd
from psychopy import logging
from itertools import product
import yaml
from session import HCPMovieELSession,HCPMovieELSessionGrading, HCPMovieELSessionLabeling


base_settings  = yaml.load(open('base_settings.yaml'), Loader=yaml.FullLoader)
rootpath = base_settings['path']['rootpath']
rootpath_video = base_settings['path']['rootpath_video']
stimuli_path = rootpath_video + base_settings['path']['stimuli_path']
settings_path = rootpath + base_settings['path']['settings_path']
output_path = rootpath + base_settings['path']['output_path']

parser = argparse.ArgumentParser()
parser.add_argument('subject', default=None, nargs='?')
parser.add_argument('run', default=None, nargs='?')
parser.add_argument('eyelink', default=False, nargs='?')

cmd_args = parser.parse_args()
subject, run, eyelink = cmd_args.subject, cmd_args.run, cmd_args.eyelink


if subject is None:
    subject = input('Subject? (5): ')
    subject = 5 if subject == '' else subject

if run is None:
    run = input('Run? (10): ')
    run = 10 if run == '' else run
elif run == '10':
    run = 10


if eyelink:
    eyetracker_on = True
    logging.warn("Using eyetracker")
else:
    eyetracker_on = False
    logging.warn("Using NO eyetracker")

group_number = subject
session_number = run


output_str = f'sub-{subject}_run-{run}_task-movie' 
#load settings from the yaml file accourding to the group number and session number
setting_path = settings_path + 'labeling_experiment_settings_sub_' + str(group_number) + '_run_' + str(session_number) + '.yml'
print(setting_path)

session_object = HCPMovieELSessionLabeling(output_str=output_str,
                            output_dir= output_path,
                            settings_file=setting_path,
                            eyetracker_on=eyetracker_on)
session_object.create_trials()
logging.warn(f'Writing results to: {op.join(session_object.output_dir, session_object.output_str)}')
session_object.run()
session_object.close()
#session_object.save_results()








