import numpy as np
import subprocess
import os
import time
from exptools2.core import PylinkEyetrackerSession
from stimuli import FixationBullsEye
from trial import (
    HCPMovieELTrial,
    InstructionTrial,
    DummyWaiterTrial,
    OutroTrial,
    HCPMovieELTrialGrading,
    HCPMovieELTrialLabeling,
)
from psychopy.visual import MovieStim3
import pandas as pd
from pathlib import Path
import yaml

try:
    from psychtoolbox import audio
    import psychtoolbox as ptb

except Exception:
    raise "psychtoolbox audio failed to import"
try:
    import soundfile as sf
except Exception:
    raise "soundfile not working"
from psychopy import sound

import aot

def save_grades_to_csv(grades, name):
    df = pd.DataFrame.from_dict(grades, orient="index")
    df.to_csv(name + ".csv")


def get_movie_length(filename):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(filename),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return float(result.stdout)


class HCPMovieELSession(PylinkEyetrackerSession):
    def __init__(
        self,
        output_str: str,
        output_dir: Path,
        core_settings_file: Path,
        run_settings_file: Path,
        eyetracker_on: bool = True,
        training_mode: bool = False,
    ):
        """Initializes StroopSession object.

        Parameters
        ----------
        output_str : str 
            Basename for all output-files (like logs), e.g., "sub-01_task-stroop_run-1"
        output_dir : str
            Path to desired output-directory (default: None, which results in $pwd/logs)
        core_settings_file : str
            Path to yaml-file with settings (default: None, which results in the package's
            default settings file (in data/default_settings.yml)
        run_settings_file : str
            Path to yaml-file with settings for this run (no default)
        """

        super().__init__(
            output_str,
            output_dir=output_dir,
            settings_file=core_settings_file,
            eyetracker_on=eyetracker_on,
        )  # initialize parent class!

        self.training_mode = training_mode
        # supplement this run's settings with the per-run yaml file's settings
        video_files = yaml.load(
            open(run_settings_file), Loader=yaml.FullLoader)
        self.settings['stimuli'].update(video_files['stimuli'])

        experiment_movie_duration = self.settings["stimuli"].get("experiment_movie_duration")

        self.fixation = FixationBullsEye(
            win=self.win,
            outer_radius=max(self.win.size),
            line_color=self.settings['stimuli'].get('fix_line_color'),
            line_width=self.settings['stimuli'].get('fix_line_width'),
            dot_color=self.settings['stimuli'].get('fix_fill_color'),
            dot_size=self.settings['stimuli'].get('fix_size')*self.pix_per_deg,
            dot_perimeter_size=self.settings['stimuli'].get('fix_perimeter_size')*self.pix_per_deg,
            dot_perimeter_smoothness=self.settings['stimuli'].get('fix_perimeter_smooth')
        )
        #self.error_sound = sound.Sound('A')
        #self.error_sound.play()
        #print(self.error_sound)
        #print(dir(self.error_sound))

        self.win._monitorFrameRate = self.settings["various"].get("monitor_framerate")  # 120? yaml?
        # movie_trial_nr is in range(self.n_trials) that comes from the number of movies listed in the yaml file
        # but not all of them are actually movies, some are blank trials, we have to deal with that
        self.n_trials = len(self.settings["stimuli"].get(
            "movie_files"))  # include the movdies and blank trials
        self.movies = ["blank" if self.settings["stimuli"].get("movie_files")[i] == "blank" else
                       self.settings["paths"].get("stimuli_path")
                       + "/"
                       + self.settings["stimuli"].get("movie_files")[i]
                       for i in range(len(self.settings["stimuli"].get("movie_files")))
                       ]

        # count the time for loading the movies
        start = time.perf_counter()
        # this self.movie_stims is the list that accessed by the trial class by using movie_trial_nr
        self.movie_stims = [
            "blank" if movie == "blank" else
            MovieStim3(
                self.win,
                filename=movie,
                size=self.settings["stimuli"].get(
                    "movie_size_pix",
                ),
                noAudio=True,
                fps=None,
            )
            for movie in self.movies  # movie is movie file path name
        ]

        print(
            f"loading {len(self.movies)} movies took {time.perf_counter()-start} seconds"
        )

    def create_trials(self):
        """Creates trials (ideally before running your session!)"""

        instruction_trial = InstructionTrial(
            session=self,
            trial_nr=0,
            phase_durations=[np.inf],
            txt="Please keep fixating at the center.",
            keys=["space"],
        )

        dummy_trial = DummyWaiterTrial(
            session=self,
            trial_nr=1,
            phase_durations=[
                np.inf, self.settings["design"].get("start_duration")],
            txt="Waiting for experiment to start",
        )

        self.trials = [instruction_trial, dummy_trial]

        for movie_trial_nr in range(self.n_trials):
            if self.movies[movie_trial_nr] == "blank":
                print(f"blank trial {movie_trial_nr}")
                trial = DummyWaiterTrial(
                    session=self,
                    trial_nr=2 + movie_trial_nr,
                    phase_durations=[
                        self.settings["design"].get("blank_duration")
                    ],
                    txt="",
                )
            else:
                trial = HCPMovieELTrial(
                    session=self,
                    # this trial number is not explicitly used in the trial class for movie playing
                    trial_nr=2 + movie_trial_nr,
                    phase_durations=[
                        self.settings["design"].get("pre_fix_movie_interval"),
                        self.settings["stimuli"].get("experiment_movie_duration"),
                        self.settings["design"].get("post_fix_movie_interval"),
                    ],
                    phase_names=["fix_pre", "movie", "fix_post"],
                    parameters={
                        # movie trail draw the movie by self.session.movie_stims[self.parameters["movie_index"]].draw()
                        # this movie_trail_nr is used to index the movie_stims list
                        "movie_index": movie_trial_nr,
                        "movie_duration": self.settings["stimuli"].get("experiment_movie_duration"),
                        "movie_file": self.movies[movie_trial_nr],
                    },
                    training_mode=self.training_mode
                )
            self.trials.append(trial)

        outro_trial = OutroTrial(
            session=self,
            trial_nr=len(self.trials) + 1,
            phase_durations=[self.settings["design"].get("end_duration")],
            txt="",
        )
        self.trials.append(outro_trial)
        # switch the tail of the trials(?)

    def create_trial(self):
        pass

    def run(self):
        """Runs experiment."""
        # self.create_trials()  # create them *before* running!

        if self.eyetracker_on:
            self.calibrate_eyetracker()

        self.start_experiment()

        if self.eyetracker_on:
            self.start_recording_eyetracker()
        for trial in self.trials:
            self.fixation.circle.color = self.settings['stimuli'].get('fix_fill_color')
            trial.run()

        self.close()


class HCPMovieELSessionGrading(HCPMovieELSession):

    def create_trials(self):
        """Creates trials (ideally before running your session!)"""

        instruction_trial = InstructionTrial(
            session=self,
            trial_nr=0,
            phase_durations=[np.inf],
            txt="Please press buttons to grade each videos. J for good, l for bad, K for in between",
            keys=["space"],
        )

        dummy_trial = DummyWaiterTrial(
            session=self,
            trial_nr=1,
            phase_durations=[
                np.inf, self.settings["design"].get("start_duration")],
            txt="Waiting for experiment to start",
        )

        self.trials = [instruction_trial, dummy_trial]

        for movie_trial_nr in range(self.n_trials):
            trial = HCPMovieELTrialGrading(
                session=self,
                trial_nr=2 + movie_trial_nr,
                phase_durations=[
                    self.settings["design"].get("fix_movie_interval"),
                    self.settings["stimuli"].get("experiment_movie_duration"),
                    np.inf,
                ],
                phase_names=["fix_pre", "movie", "fix_post"],
                parameters={
                    "movie_index": movie_trial_nr,
                    "movie_duration": self.settings["stimuli"].get("experiment_movie_duration"),
                    "movie_file": self.movies[movie_trial_nr],
                },
            )
            self.trials.append(trial)

        outro_trial = OutroTrial(
            session=self,
            trial_nr=len(self.trials) + 1,
            phase_durations=[self.settings["design"].get("end_duration")],
            txt="",
        )
        self.trials.append(outro_trial)

    def create_trial(self):
        pass

    def run(self):
        """Runs experiment."""
        # self.create_trials()  # create them *before* running!

        if self.eyetracker_on:
            self.calibrate_eyetracker()

        self.start_experiment()

        if self.eyetracker_on:
            self.start_recording_eyetracker()

        for trial in self.trials:
            trial.run()
            save_grades_to_csv(
                self.grades, os.path.join(
                    self.output_dir, f"{self.output_str}_grades")
            )

        self.close()


class HCPMovieELSessionLabeling(HCPMovieELSession):

    def create_trials(self):
        """Creates trials (ideally before running your session!)"""

        instruction_trial = InstructionTrial(
            session=self,
            trial_nr=0,
            phase_durations=[np.inf],
            txt="Please keep fixating at the center.",
            keys=["space"],
        )

        dummy_trial = DummyWaiterTrial(
            session=self,
            trial_nr=1,
            phase_durations=[
                np.inf, self.settings["design"].get("start_duration")],
            txt="Waiting for experiment to start",
        )

        self.trials = [instruction_trial, dummy_trial]

        for movie_trial_nr in range(self.n_trials):
            phase_durations = [
                self.settings["design"].get("fix_movie_interval"),
                self.settings["stimuli"].get("experiment_movie_duration"),
            ]
            for i in range(len(self.list_of_text)):
                phase_durations.append(np.inf)

            trial = HCPMovieELTrialLabeling(
                session=self,
                trial_nr=2 + movie_trial_nr,
                phase_durations=phase_durations,
                # phase_names=['fix_pre', 'movie', 'fix_post'],
                parameters={
                    "movie_index": movie_trial_nr,
                    "movie_duration": self.settings["stimuli"].get("experiment_movie_duration"),
                    "movie_file": self.movies[movie_trial_nr],
                },
            )
            self.trials.append(trial)

        outro_trial = OutroTrial(
            session=self,
            trial_nr=len(self.trials) + 1,
            phase_durations=[self.settings["design"].get("end_duration")],
            txt="",
        )
        self.trials.append(outro_trial)

    def create_trial(self):
        pass

    def run(self):
        """Runs experiment."""
        # self.create_trials()  # create them *before* running!

        if self.eyetracker_on:
            self.calibrate_eyetracker()

        self.start_experiment()

        if self.eyetracker_on:
            self.start_recording_eyetracker()

        # with open(os.path.join(self.output_dir, f'{self.output_str}_grades.txt'), 'w') as outfile:

        for trial in self.trials:
            trial.run()
            save_grades_to_csv(
                self.grades, os.path.join(
                    self.output_dir, f"{self.output_str}_labels")
            )

        self.close()
