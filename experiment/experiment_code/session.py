import numpy as np
import scipy.stats as ss
import subprocess, os
import time
from exptools2.core import Session, PylinkEyetrackerSession
from stimuli import FixationLines,FixationBullsEye
from trial import HCPMovieELTrial, InstructionTrial, DummyWaiterTrial, OutroTrial, HCPMovieELTrialGrading, HCPMovieELTrialLabeling
from psychopy.visual import ImageStim, MovieStim3
from psychopy.visual import VlcMovieStim
import pandas as pd

def save_grades_to_csv(grades,name):
    df = pd.DataFrame.from_dict(grades, orient='index')
    df.to_csv(name+'.csv')


def get_movie_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", str(filename)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)


class HCPMovieELSession(PylinkEyetrackerSession): 
    def __init__(self, output_str, output_dir, settings_file, eyetracker_on=True):
        """ Initializes StroopSession object. 
      
        Parameters
        ----------
        output_str : str
            Basename for all output-files (like logs), e.g., "sub-01_task-stroop_run-1"
        output_dir : str
            Path to desired output-directory (default: None, which results in $pwd/logs)
        settings_file : str
            Path to yaml-file with settings (default: None, which results in the package's
            default settings file (in data/default_settings.yml)
        """
        super().__init__(output_str, output_dir=output_dir, settings_file=settings_file, eyetracker_on=eyetracker_on)  # initialize parent class!
        
        self.fixation = FixationBullsEye(win=self.win,
                                    circle_radius=self.settings['stimuli'].get('aperture_radius')*2,
                                    color=(1, 1, 1))
    
        self.report_fixation = FixationBullsEye(win=self.win,
                                    circle_radius=self.settings['stimuli'].get('aperture_radius')*2,
                                    color=(1, 1, 1))
        

        self.win._monitorFrameRate = 60#################################################################### 120? yaml?
        self.n_trials = len(self.settings['stimuli'].get('movie_files'))
        self.movies = [os.path.join(os.path.abspath(os.getcwd()), 'movs', self.settings['stimuli'].get('movie_files')[i]) 
                                                for i in range(len(self.settings['stimuli'].get('movie_files')))]
        #self.movie_durations = [get_movie_length(movie) for movie in self.movies]
        self.movie_durations = [3.0 for movie in self.movies]###############################################################################
        print(f'movie duration for this run: {self.movie_durations}')

        #count the time for loading the movies     
        start = time.time()
        self.movie_stims = [MovieStim3(self.win, 
                            filename=movie,     
                            size=self.settings['stimuli'].get('movie_size_pix',),
                            noAudio=True,
                            fps=None,
                            ) for movie in self.movies]
        #self.movie_stims = [VlcMovieStim(self.win, filename=movie, size=self.settings['stimuli'].get('movie_size_pix')) for movie in self.movies]
        end = time.time()
        print(f'loading {len(self.movies)}movies took {end-start} seconds') 

    def create_trials(self):
        """ Creates trials (ideally before running your session!) """

        instruction_trial = InstructionTrial(session=self, 
                                            trial_nr=0, 
                                            phase_durations=[np.inf],
                                            txt='Please keep fixating at the center.', 
                                            keys=['space'])

        dummy_trial = DummyWaiterTrial(session=self, 
                                            trial_nr=1, 
                                            phase_durations=[np.inf, self.settings['design'].get('start_duration')],
                                            txt='Waiting for experiment to start')



        self.trials = [instruction_trial, dummy_trial] 


        for movie_trial_nr in range(self.n_trials):
            trial = HCPMovieELTrial(session=self,  
                                    trial_nr=2+movie_trial_nr, 
                                    phase_durations=[self.settings['design'].get('pre_fix_movie_interval'), self.movie_durations[movie_trial_nr], self.settings['design'].get('post_fix_movie_interval')], 
                                    phase_names=['fix_pre', 'movie', 'fix_post'],
                                    parameters={'movie_index':movie_trial_nr, 'movie_duration':self.movie_durations[movie_trial_nr], 'movie_file': self.movies[movie_trial_nr]})
            self.trials.append(trial)

        outro_trial = OutroTrial(session=self, 
                                trial_nr=len(self.trials)+1, 
                                phase_durations=[self.settings['design'].get('end_duration')],
                                txt='')
        self.trials.append(outro_trial)
        #switch the tail of the trials(?) 

    def create_trial(self):
        pass

    def run(self):
        """ Runs experiment. """   
        # self.create_trials()  # create them *before* running! 

        if self.eyetracker_on:
            self.calibrate_eyetracker()

        self.start_experiment()

        if self.eyetracker_on:
            self.start_recording_eyetracker()
        for trial in self.trials:
            trial.run()

        self.close()
    


class HCPMovieELSessionGrading(PylinkEyetrackerSession):
    def __init__(self, output_str, output_dir, settings_file, eyetracker_on=True):
        """ Initializes StroopSession object. 
      
        Parameters
        ----------
        output_str : str
            Basename for all output-files (like logs), e.g., "sub-01_task-stroop_run-1"
        output_dir : str
            Path to desired output-directory (default: None, which results in $pwd/logs)
        settings_file : str
            Path to yaml-file with settings (default: None, which results in the package's
            default settings file (in data/default_settings.yml)
        """ 
        super().__init__(output_str, output_dir=output_dir, settings_file=settings_file, eyetracker_on=eyetracker_on)  # initialize parent class!
        
        self.fixation = FixationLines(win=self.win, 
                                    circle_radius=self.settings['stimuli'].get('aperture_radius')*2,
                                    color=(1, -1, -1), 
                                    line_width=self.settings['stimuli'].get('fix_line_width'))
        '''
        self.fixation = FixationCross(win=self.win, 
                                    circle_radius=self.settings['stimuli'].get('fix_radius')*2,
                                    color=self.settings['stimuli'].get('fix_color'), 
                                    line_width=self.settings['stimuli'].get('fix_line_width'))
        '''      
        self.report_fixation = FixationLines(win=self.win, 
                                    circle_radius=self.settings['stimuli'].get('fix_radius')*2,
                                    color=self.settings['stimuli'].get('fix_color'), 
                                    line_width=self.settings['stimuli'].get('fix_line_width'))
        #fixation mark when the movie is playing
        
        self.n_trials = len(self.settings['stimuli'].get('movie_files'))
        self.movies = [os.path.join(os.path.abspath(os.getcwd()), 'movs', self.settings['stimuli'].get('movie_files')[i]) 
                                                for i in range(len(self.settings['stimuli'].get('movie_files')))]
        
        #self.movie_durations = [2.0 for movie in self.movies]#####################not 2.0
        self.movie_durations = [get_movie_length(movie) for movie in self.movies]# it is grading
        self.grades = {}
        #print(f'movie duration for this run: {self.movie_durations}')
        self.win._monitorFrameRate = 60#################################################################### 120? yaml?
        #count the time for loading the movies     
        start = time.time()
        #self.movie_stims = Parallel(n_jobs=-1,backend='multiprocessing')(delayed(MovieStim3)(self.win, filename=movie, size=self.settings['stimuli'].get('movie_size_pix')) for movie in self.movies)
        self.movie_stims = [MovieStim3(self.win, 
                            filename=movie,     
                            size=self.settings['stimuli'].get('movie_size_pix',),
                            noAudio=True, 
                            fps=None,
                            ) for movie in self.movies]
        #self.movie_stims = []
        #for i in range(10):
        #    self.movie_stims.append(MovieStim3(self.win, filename=self.movies[i], size=self.settings['stimuli'].get('movie_size_pix')))
        #[MovieStim3(self.win, filename=self.movies[0], size=self.settings['stimuli'].get('movie_size_pix'))]
        #self.movie_stims = [VlcMovieStim(self.win, filename=movie, size=self.settings['stimuli'].get('movie_size_pix')) for movie in self.movies]
        end = time.time()
        print(f'loading {len(self.movies)}movies took {end-start} seconds') 

    def create_trials(self):
        """ Creates trials (ideally before running your session!) """

        instruction_trial = InstructionTrial(session=self, 
                                            trial_nr=0, 
                                            phase_durations=[np.inf],
                                            txt='Please keep fixating at the center.', 
                                            keys=['space'])

        dummy_trial = DummyWaiterTrial(session=self, 
                                            trial_nr=1, 
                                            phase_durations=[np.inf, self.settings['design'].get('start_duration')],
                                            txt='Waiting for experiment to start')



        self.trials = [instruction_trial, dummy_trial] 


        for movie_trial_nr in range(self.n_trials):
            trial = HCPMovieELTrialGrading(session=self, 
                                    trial_nr=2+movie_trial_nr, 
                                    phase_durations=[self.settings['design'].get('fix_movie_interval'), self.movie_durations[movie_trial_nr],np.inf],#self.settings['design'].get('fix_movie_interval')], 
                                    phase_names=['fix_pre', 'movie', 'fix_post'],
                                    parameters={'movie_index':movie_trial_nr, 'movie_duration':self.movie_durations[movie_trial_nr], 'movie_file': self.movies[movie_trial_nr]})
            self.trials.append(trial)

        outro_trial = OutroTrial(session=self, 
                                trial_nr=len(self.trials)+1, 
                                phase_durations=[self.settings['design'].get('end_duration')],
                                txt='')
        self.trials.append(outro_trial)

    def create_trial(self):
        pass

    def run(self):
        """ Runs experiment. """   
        # self.create_trials()  # create them *before* running! 

        if self.eyetracker_on:
            self.calibrate_eyetracker()

        self.start_experiment()

        if self.eyetracker_on:
            self.start_recording_eyetracker()

        #with open(os.path.join(self.output_dir, f'{self.output_str}_grades.txt'), 'w') as outfile:

        for trial in self.trials:
            trial.run()
            save_grades_to_csv(self.grades, os.path.join(self.output_dir, f'{self.output_str}_grades'))
        
                
        self.close()
    




class HCPMovieELSessionLabeling(PylinkEyetrackerSession):
    def __init__(self, output_str, output_dir, settings_file, eyetracker_on=True):
        """ Initializes StroopSession object. 
      
        Parameters
        ----------
        output_str : str
            Basename for all output-files (like logs), e.g., "sub-01_task-stroop_run-1"
        output_dir : str
            Path to desired output-directory (default: None, which results in $pwd/logs)
        settings_file : str
            Path to yaml-file with settings (default: None, which results in the package's
            default settings file (in data/default_settings.yml)
        """ 
        super().__init__(output_str, output_dir=output_dir, settings_file=settings_file, eyetracker_on=eyetracker_on)  # initialize parent class!
        
        self.fixation = FixationLines(win=self.win,  
                                    circle_radius=self.settings['stimuli'].get('aperture_radius')*2,
                                    color=(1, -1, -1), 
                                    line_width=self.settings['stimuli'].get('fix_line_width'))
        '''
        self.fixation = FixationCross(win=self.win, 
                                    circle_radius=self.settings['stimuli'].get('fix_radius')*2,
                                    color=self.settings['stimuli'].get('fix_color'), 
                                    line_width=self.settings['stimuli'].get('fix_line_width'))
        '''      
        self.report_fixation = FixationLines(win=self.win, 
                                    circle_radius=self.settings['stimuli'].get('fix_radius')*2,
                                    color=self.settings['stimuli'].get('fix_color'), 
                                    line_width=self.settings['stimuli'].get('fix_line_width'))
        #fixation mark when the movie is playing
        
        self.n_trials = len(self.settings['stimuli'].get('movie_files'))
        self.movies = [os.path.join(os.path.abspath(os.getcwd()), 'movs', self.settings['stimuli'].get('movie_files')[i]) 
                                                for i in range(len(self.settings['stimuli'].get('movie_files')))]
        
        #self.movie_durations = [2.0 for movie in self.movies]#####################not 2.0
        self.movie_durations = [get_movie_length(movie) for movie in self.movies]# it is grading
        self.list_of_text = self.settings['various'].get('text_list')
        print(self.list_of_text)
        self.num_labels = len(self.list_of_text)
        self.grades = {}

        #print(f'movie duration for this run: {self.movie_durations}')
        self.win._monitorFrameRate = 60#################################################################### 120? yaml?
        #count the time for loading the movies     
        start = time.time()
        #self.movie_stims = Parallel(n_jobs=-1,backend='multiprocessing')(delayed(MovieStim3)(self.win, filename=movie, size=self.settings['stimuli'].get('movie_size_pix')) for movie in self.movies)
        self.movie_stims = [MovieStim3(self.win, 
                            filename=movie,     
                            size=self.settings['stimuli'].get('movie_size_pix',),
                            noAudio=True, 
                            fps=None,
                            ) for movie in self.movies]
        #self.movie_stims = []
        #for i in range(10):
        #    self.movie_stims.append(MovieStim3(self.win, filename=self.movies[i], size=self.settings['stimuli'].get('movie_size_pix')))
        #[MovieStim3(self.win, filename=self.movies[0], size=self.settings['stimuli'].get('movie_size_pix'))]
        #self.movie_stims = [VlcMovieStim(self.win, filename=movie, size=self.settings['stimuli'].get('movie_size_pix')) for movie in self.movies]
        end = time.time()
        print(f'loading {len(self.movies)}movies took {end-start} seconds') 

    def create_trials(self):
        """ Creates trials (ideally before running your session!) """

        instruction_trial = InstructionTrial(session=self, 
                                            trial_nr=0, 
                                            phase_durations=[np.inf],
                                            txt='Please keep fixating at the center.', 
                                            keys=['space'])

        dummy_trial = DummyWaiterTrial(session=self, 
                                            trial_nr=1, 
                                            phase_durations=[np.inf, self.settings['design'].get('start_duration')],
                                            txt='Waiting for experiment to start')



        self.trials = [instruction_trial, dummy_trial]  


        for movie_trial_nr in range(self.n_trials):
            phase_durations = [self.settings['design'].get('fix_movie_interval'), self.movie_durations[movie_trial_nr]]
            for i in range(len(self.list_of_text)):
                phase_durations.append(np.inf)

            trial = HCPMovieELTrialLabeling(session=self, 
                                    trial_nr=2+movie_trial_nr, 
                                    #phase_durations=[self.settings['design'].get('fix_movie_interval'), self.movie_durations[movie_trial_nr],np.inf],#self.settings['design'].get('fix_movie_interval')], 
                                    phase_durations=phase_durations,
                                    #phase_names=['fix_pre', 'movie', 'fix_post'],
                                    parameters={'movie_index':movie_trial_nr, 'movie_duration':self.movie_durations[movie_trial_nr], 'movie_file': self.movies[movie_trial_nr]})
            self.trials.append(trial)

        outro_trial = OutroTrial(session=self, 
                                trial_nr=len(self.trials)+1, 
                                phase_durations=[self.settings['design'].get('end_duration')],
                                txt='')
        self.trials.append(outro_trial)

    def create_trial(self):
        pass

    def run(self):
        """ Runs experiment. """   
        # self.create_trials()  # create them *before* running! 

        if self.eyetracker_on:
            self.calibrate_eyetracker()

        self.start_experiment()

        if self.eyetracker_on:
            self.start_recording_eyetracker()

        #with open(os.path.join(self.output_dir, f'{self.output_str}_grades.txt'), 'w') as outfile:

        for trial in self.trials:
            trial.run()
            save_grades_to_csv(self.grades, os.path.join(self.output_dir, f'{self.output_str}_labels'))
        
                
        self.close()