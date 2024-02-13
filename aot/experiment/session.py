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
    HCPMovieELTrialMemory,
    HCPMovieELTrialLearning,
    HCPMovieELTrialEyetracking,
)
from psychopy.visual import MovieStim3
from psychopy.visual import ImageStim
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
        video_files = yaml.load(open(run_settings_file),
                                Loader=yaml.FullLoader)
        self.settings["stimuli"].update(video_files["stimuli"])

        experiment_movie_duration = self.settings["stimuli"].get(
            "experiment_movie_duration"
        )

        # we dont need this for lab computer but required by my laptop????
        # check whether the program is running on the my laptop
        if os.path.exists("/Users/shufanzhang/Documents/PhD/Arrow_of_time"):
            self.pix_per_deg = self.win.size[0] / self.win.monitor.getWidth()

        originalsize = self.settings["stimuli"].get("movie_size_pix")
        shrink_factor = self.settings["stimuli"].get("shrink_factor")
        display_size = [l*shrink_factor for l in originalsize]
        self.shiftedpos = (0, -originalsize[1]*(1-shrink_factor)/2)

        self.fixation = FixationBullsEye(
            win=self.win,
            outer_radius=max(self.win.size),
            line_color=self.settings["stimuli"].get("fix_line_color"),
            line_width=self.settings["stimuli"].get("fix_line_width"),
            dot_color=self.settings["stimuli"].get("fix_fill_color"),
            dot_size=self.settings["stimuli"].get(
                "fix_size") * self.pix_per_deg,
            dot_perimeter_size=self.settings["stimuli"].get(
                "fix_perimeter_size")
            * self.pix_per_deg,
            dot_perimeter_smoothness=self.settings["stimuli"].get(
                "fix_perimeter_smooth"
            ),
            pos=self.shiftedpos
        )

        # self.error_sound = sound.Sound('A')
        # self.error_sound.play()
        # print(self.error_sound)
        # print(dir(self.error_sound))

        self.fourcount = 1

        self.win._monitorFrameRate = self.settings["various"].get(
            "monitor_framerate"
        )  # 120? yaml?
        # movie_trial_nr is in range(self.n_trials) that comes from the number of movies listed in the yaml file
        # but not all of them are actually movies, some are blank trials, we have to deal with that
        self.n_trials = len(
            self.settings["stimuli"].get("movie_files")
        )  # include the movdies and blank trials
        if os.path.exists("/Users/shufanzhang/Documents/PhD/Arrow_of_time"):
            self.movies = [
                "blank"
                if self.settings["stimuli"].get("movie_files")[i] == "blank"
                else self.settings["paths"].get("stimuli_path")
                + "/"
                + self.settings["stimuli"].get("movie_files")[i]
                for i in range(len(self.settings["stimuli"].get("movie_files")))
            ]
        elif os.path.exists(self.settings['paths'].get('stimuli_path_spinoza1')):
            self.movies = [
                "blank"
                if self.settings["stimuli"].get("movie_files")[i] == "blank"
                else self.settings["paths"].get("stimuli_path_spinoza1")
                + "/"
                + self.settings["stimuli"].get("movie_files")[i]
                for i in range(len(self.settings["stimuli"].get("movie_files")))
            ]
        elif os.path.exists(self.settings['paths'].get('stimuli_path_spinoza2')):
            self.movies = [
                "blank"
                if self.settings["stimuli"].get("movie_files")[i] == "blank"
                else self.settings["paths"].get("stimuli_path_spinoza2")
                + "/"
                + self.settings["stimuli"].get("movie_files")[i]
                for i in range(len(self.settings["stimuli"].get("movie_files")))
            ]
        print(self.movies)

        # count the time for loading the movies
        start = time.perf_counter()
        self.movie_stims = [
            "blank"
            if movie == "blank"
            else MovieStim3(
                self.win,
                filename=movie,
                size=display_size,
                noAudio=True,
                fps=None,
                pos=self.shiftedpos
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
            pos=self.shiftedpos
        )

        dummy_trial = DummyWaiterTrial(
            session=self,
            trial_nr=1,
            phase_durations=[
                np.inf, self.settings["design"].get("start_duration")],
            txt="",
        )

        self.trials = [instruction_trial, dummy_trial]

        for movie_trial_nr in range(self.n_trials):
            if self.movies[movie_trial_nr] == "blank":
                blank = 1
            else:
                blank = 0

            if (movie_trial_nr+4) % 4 == 0:
                phase_durations = [
                    self.settings["design"].get(
                        "pre_fix_movie_interval"),  # 90
                    self.settings["stimuli"].get("experiment_movie_duration"),
                    self.settings["design"].get(
                        "post_fix_movie_interval"),  # 0.1
                ]
            else:
                phase_durations = [
                    1,
                    self.settings["stimuli"].get("experiment_movie_duration"),
                    self.settings["design"].get(
                        "post_fix_movie_interval"),  # 0.1
                ]
            trial = HCPMovieELTrial(
                session=self,
                # this trial number is not explicitly used in the trial class for movie playing
                trial_nr=2 + movie_trial_nr,
                phase_durations=phase_durations,
                phase_names=["fix_pre", "movie", "fix_post"],
                parameters={
                    # movie trail draw the movie by self.session.movie_stims[self.parameters["movie_index"]].draw()
                    # this movie_trail_nr is used to index the movie_stims list
                    "movie_index": movie_trial_nr,
                    "movie_duration": self.settings["stimuli"].get(
                        "experiment_movie_duration"
                    ),
                    "movie_file": self.movies[movie_trial_nr],
                    "blank": blank,
                },
                training_mode=self.training_mode,
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
        self.fourtcount = 0

        if self.eyetracker_on:
            self.start_recording_eyetracker()
        '''
        for trial in self.trials:
            self.fixation.circle.color = self.settings["stimuli"].get("fix_fill_color")
            trial.run()
            if self.fourcount == 4:
                self.forcount = 0
            self.fourcount += 1
        '''
        for trialind in range(len(self.trials)):
            trial = self.trials[trialind]
            if trialind == 2:
                self.fourcount = 4
                self.fixation.circle.color = self.settings["stimuli"].get(
                    "fix_fill_color")
                trial.run()
                if self.fourcount == 4:
                    self.fourcount = 0
                self.fourcount += 1
            else:
                self.fixation.circle.color = self.settings["stimuli"].get(
                    "fix_fill_color")
                trial.run()
                if self.fourcount == 4:
                    self.fourcount = 0
                self.fourcount += 1

        self.close()


class HCPMovieELSessionEyetracking(PylinkEyetrackerSession):
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
        video_files = yaml.load(open(run_settings_file),
                                Loader=yaml.FullLoader)
        self.settings["stimuli"].update(video_files["stimuli"])

        experiment_movie_duration = self.settings["stimuli"].get(
            "experiment_movie_duration"
        )

        if os.path.exists("/Users/shufanzhang/Documents/PhD/Arrow_of_time"):
            self.pix_per_deg = self.win.size[0] / self.win.monitor.getWidth()
        elif os.path.exists("/home/egter/Projects/arrow_of_time_experiment/aot"):
            self.pix_per_deg = self.win.size[0] / self.win.monitor.getWidth()

        self.fixation = FixationBullsEye(
            win=self.win,
            outer_radius=max(self.win.size),
            line_color=self.settings["stimuli"].get("fix_line_color"),
            line_width=self.settings["stimuli"].get("fix_line_width"),
            dot_color=self.settings["stimuli"].get("fix_fill_color"),
            dot_size=self.settings["stimuli"].get(
                "fix_size") * self.pix_per_deg,
            dot_perimeter_size=self.settings["stimuli"].get(
                "fix_perimeter_size")
            * self.pix_per_deg,
            dot_perimeter_smoothness=self.settings["stimuli"].get(
                "fix_perimeter_smooth"
            ),
        )

        # we dont need this for lab computer but required by my laptop????
        # check whether the program is running on the my laptop
        if os.path.exists("/Users/shufanzhang/Documents/PhD/Arrow_of_time"):
            self.pix_per_deg = self.win.size[0] / self.win.monitor.getWidth()

        originalsize = self.settings["stimuli"].get("movie_size_pix")

        # self.error_sound = sound.Sound('A')
        # self.error_sound.play()
        # print(self.error_sound)
        # print(dir(self.error_sound))

        self.fourcount = 1

        self.win._monitorFrameRate = self.settings["various"].get(
            "monitor_framerate"
        )  # 120? yaml?
        # movie_trial_nr is in range(self.n_trials) that comes from the number of movies listed in the yaml file
        # but not all of them are actually movies, some are blank trials, we have to deal with that
        self.n_trials = len(
            self.settings["stimuli"].get("movie_files")
        )  # include the movdies and blank trials
        if os.path.exists("/Users/shufanzhang/Documents/PhD/Arrow_of_time"):
            self.movies = [
                "blank"
                if self.settings["stimuli"].get("movie_files")[i] == "blank"
                else self.settings["paths"].get("stimuli_path")
                + "/"
                + self.settings["stimuli"].get("movie_files")[i]
                for i in range(len(self.settings["stimuli"].get("movie_files")))
            ]
        elif os.path.exists(self.settings['paths'].get('stimuli_path_spinoza1')):
            self.movies = [
                "blank"
                if self.settings["stimuli"].get("movie_files")[i] == "blank"
                else self.settings["paths"].get("stimuli_path_spinoza1")
                + "/"
                + self.settings["stimuli"].get("movie_files")[i]
                for i in range(len(self.settings["stimuli"].get("movie_files")))
            ]
        elif os.path.exists(self.settings['paths'].get('stimuli_path_spinoza2')):
            self.movies = [
                "blank"
                if self.settings["stimuli"].get("movie_files")[i] == "blank"
                else self.settings["paths"].get("stimuli_path_spinoza2")
                + "/"
                + self.settings["stimuli"].get("movie_files")[i]
                for i in range(len(self.settings["stimuli"].get("movie_files")))
            ]
        print(self.movies)

        # count the time for loading the movies
        start = time.perf_counter()
        self.movie_stims = [
            "blank"
            if movie == "blank"
            else MovieStim3(
                self.win,
                filename=movie,
                size=originalsize,
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
            txt="Feel free to look around to understand the video.",
            keys=["space"],
        )

        dummy_trial = DummyWaiterTrial(
            session=self,
            trial_nr=1,
            phase_durations=[
                1, 1],
            txt="",
        )

        self.trials = [instruction_trial, dummy_trial]

        for movie_trial_nr in range(self.n_trials):
            if self.movies[movie_trial_nr] == "blank":
                blank = 1
            else:
                blank = 0

            if (movie_trial_nr+4) % 4 == 0:
                phase_durations = [
                    np.inf,
                    self.settings["stimuli"].get("experiment_movie_duration"),
                    self.settings["design"].get(
                        "post_fix_movie_interval"),  # 0.1
                ]
            else:
                phase_durations = [
                    np.inf,
                    self.settings["stimuli"].get("experiment_movie_duration"),
                    self.settings["design"].get(
                        "post_fix_movie_interval"),  # 0.1
                ]
            trial = HCPMovieELTrialEyetracking(
                session=self,
                # this trial number is not explicitly used in the trial class for movie playing
                trial_nr=2 + movie_trial_nr,
                phase_durations=phase_durations,
                phase_names=["fix_pre", "movie", "fix_post"],
                parameters={
                    # movie trail draw the movie by self.session.movie_stims[self.parameters["movie_index"]].draw()
                    # this movie_trail_nr is used to index the movie_stims list
                    "movie_index": movie_trial_nr,
                    "movie_duration": self.settings["stimuli"].get(
                        "experiment_movie_duration"
                    ),
                    "movie_file": self.movies[movie_trial_nr],
                    "blank": blank,
                },
                training_mode=self.training_mode,
            )
            self.trials.append(trial)

        outro_trial = OutroTrial(
            session=self,
            trial_nr=len(self.trials) + 1,
            phase_durations=[self.settings["design"].get("end_duration")],
            txt="End of this run",
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
        self.fourtcount = 0

        if self.eyetracker_on:
            self.start_recording_eyetracker()
        '''
        for trial in self.trials:
            self.fixation.circle.color = self.settings["stimuli"].get("fix_fill_color")
            trial.run()
            if self.fourcount == 4:
                self.forcount = 0
            self.fourcount += 1
        '''
        for trialind in range(len(self.trials)):
            trial = self.trials[trialind]
            if trialind == 2:
                self.fourcount = 4
                trial.run()
                if self.fourcount == 4:
                    self.fourcount = 0
                self.fourcount += 1
            else:
                trial.run()
                if self.fourcount == 4:
                    self.fourcount = 0
                self.fourcount += 1

        self.close()


class HCPMovieELSessionLearning(PylinkEyetrackerSession):
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
        video_files = yaml.load(open(run_settings_file),
                                Loader=yaml.FullLoader)
        self.settings["stimuli"].update(video_files["stimuli"])

        experiment_movie_duration = self.settings["stimuli"].get(
            "experiment_movie_duration"
        )

        # we dont need this for lab computer but required by my laptop????
        # check whether the program is running on the my laptop
        if os.path.exists("/Users/shufanzhang/Documents/PhD/Arrow_of_time"):
            self.pix_per_deg = self.win.size[0] / self.win.monitor.getWidth()

        self.fixation = FixationBullsEye(
            win=self.win,
            outer_radius=max(self.win.size),
            line_color=self.settings["stimuli"].get("fix_line_color"),
            line_width=self.settings["stimuli"].get("fix_line_width"),
            dot_color=self.settings["stimuli"].get("fix_fill_color"),
            dot_size=self.settings["stimuli"].get(
                "fix_size") * self.pix_per_deg,
            dot_perimeter_size=self.settings["stimuli"].get(
                "fix_perimeter_size")
            * self.pix_per_deg,
            dot_perimeter_smoothness=self.settings["stimuli"].get(
                "fix_perimeter_smooth"
            ),
        )
        # self.error_sound = sound.Sound('A')
        # self.error_sound.play()
        # print(self.error_sound)
        # print(dir(self.error_sound))

        self.fourcount = 1

        self.win._monitorFrameRate = self.settings["various"].get(
            "monitor_framerate"
        )  # 120? yaml?
        # movie_trial_nr is in range(self.n_trials) that comes from the number of movies listed in the yaml file
        # but not all of them are actually movies, some are blank trials, we have to deal with that
        self.n_trials = len(
            self.settings["stimuli"].get("movie_files")
        )  # include the movdies and blank trials
        if os.path.exists("/Users/shufanzhang/Documents/PhD/Arrow_of_time"):
            self.movies = [
                "blank"
                if self.settings["stimuli"].get("movie_files")[i] == "blank"
                else self.settings["paths"].get("stimuli_path")
                + "/"
                + self.settings["stimuli"].get("movie_files")[i]
                for i in range(len(self.settings["stimuli"].get("movie_files")))
            ]
        # the eyetracking training is using the old videos
        elif os.path.exists(self.settings['paths'].get('oldstimuli_path_spinoza1')):
            self.movies = [
                "blank"
                if self.settings["stimuli"].get("movie_files")[i] == "blank"
                else self.settings["paths"].get("oldstimuli_path_spinoza1")
                + "/"
                + self.settings["stimuli"].get("movie_files")[i]
                for i in range(len(self.settings["stimuli"].get("movie_files")))
            ]
        elif os.path.exists(self.settings['paths'].get('oldstimuli_path_spinoza2')):
            self.movies = [
                "blank"
                if self.settings["stimuli"].get("movie_files")[i] == "blank"
                else self.settings["paths"].get("oldstimuli_path_spinoza2")
                + "/"
                + self.settings["stimuli"].get("movie_files")[i]
                for i in range(len(self.settings["stimuli"].get("movie_files")))
            ]
        print(self.movies)

        # count the time for loading the movies
        start = time.perf_counter()
        # this self.movie_stims is the list that accessed by the trial class by using movie_trial_nr
        originalsize = self.settings["stimuli"].get("movie_size_pix")
        # shrink_factor = self.settings["stimuli"].get("shrink_factor")
        # display_size = [l*shrink_factor for l in size]
        self.movie_stims = [
            "blank"
            if movie == "blank"
            else MovieStim3(
                self.win,
                filename=movie,
                size=originalsize,
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
            txt="Please keep fixating at the center, Otherwise the fixation point will turn red with beep sound.Try to blink only during the blank",
            keys=["space"],
        )

        dummy_trial = DummyWaiterTrial(
            session=self,
            trial_nr=1,
            phase_durations=[
                np.inf, self.settings["design"].get("start_duration")],
            txt="",
        )

        self.trials = [instruction_trial]

        for movie_trial_nr in range(self.n_trials):
            if self.movies[movie_trial_nr] == "blank":
                blank = 1
            else:
                blank = 0

            phase_durations = [
                1,
                self.settings["stimuli"].get("experiment_movie_duration"),
                self.settings["design"].get(
                    "post_fix_movie_interval"),  # 0.1
            ]
            trial = HCPMovieELTrialLearning(
                session=self,
                # this trial number is not explicitly used in the trial class for movie playing
                trial_nr=1 + movie_trial_nr,
                phase_durations=phase_durations,
                phase_names=["fix_pre", "movie", "fix_post"],
                parameters={
                    # movie trail draw the movie by self.session.movie_stims[self.parameters["movie_index"]].draw()
                    # this movie_trail_nr is used to index the movie_stims list
                    "movie_index": movie_trial_nr,
                    "movie_duration": self.settings["stimuli"].get(
                        "experiment_movie_duration"
                    ),
                    "movie_file": self.movies[movie_trial_nr],
                    "blank": blank,
                },
                training_mode=self.training_mode,
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
        self.fourtcount = 0

        if self.eyetracker_on:
            self.start_recording_eyetracker()
        '''
        for trial in self.trials:
            self.fixation.circle.color = self.settings["stimuli"].get("fix_fill_color")
            trial.run()
            if self.fourcount == 4:
                self.forcount = 0
            self.fourcount += 1
        '''
        for trialind in range(len(self.trials)):
            trial = self.trials[trialind]
            if trialind == 2:
                self.fourcount = 4
                self.fixation.circle.color = self.settings["stimuli"].get(
                    "fix_fill_color")
                trial.run()
                if self.fourcount == 4:
                    self.fourcount = 0
                self.fourcount += 1
            else:
                self.fixation.circle.color = self.settings["stimuli"].get(
                    "fix_fill_color")
                trial.run()
                if self.fourcount == 4:
                    self.fourcount = 0
                self.fourcount += 1

        self.close()


class HCPMovieELSessionMemory(PylinkEyetrackerSession):
    def __init__(
        self,
        output_str: str,
        output_dir: Path,
        core_settings_file: Path,
        run_settings_file: Path,
        eyetracker_on: bool = True,
    ):
        super().__init__(
            output_str,
            output_dir=output_dir,
            settings_file=core_settings_file,
            eyetracker_on=eyetracker_on,
        )  # initialize parent class!

        # check whether the program is running on the my laptop
        if os.path.exists("/Users/shufanzhang/Documents/PhD"):
            self.pix_per_deg = self.win.size[0] / self.win.monitor.getWidth()
        elif os.path.exists("/home/egter/Projects/arrow_of_time_experiment/aot"):
            self.pix_per_deg = self.win.size[0] / self.win.monitor.getWidth()

        self.fixation = FixationBullsEye(
            win=self.win,
            outer_radius=max(self.win.size),
            line_color=self.settings["stimuli"].get("fix_line_color"),
            line_width=self.settings["stimuli"].get("fix_line_width"),
            dot_color=self.settings["stimuli"].get("fix_fill_color"),
            dot_size=self.settings["stimuli"].get(
                "fix_size") * self.pix_per_deg,
            dot_perimeter_size=self.settings["stimuli"].get(
                "fix_perimeter_size")
            * self.pix_per_deg,
            dot_perimeter_smoothness=self.settings["stimuli"].get(
                "fix_perimeter_smooth"
            ),
        )
        self.grades = {}
        picture_files = yaml.load(
            open(run_settings_file), Loader=yaml.FullLoader)
        self.settings["stimuli"].update(picture_files["stimuli"])
        self.win._monitorFrameRate = self.settings["various"].get(
            "monitor_framerate"
        )  # 120? yaml?
        # movie_trial_nr is in range(self.n_trials) that comes from the number of movies listed in the yaml file
        # but not all of them are actually movies, some are blank trials, we have to deal with that
        self.n_trials = len(
            self.settings["stimuli"].get("picture_files")
        )  # include the movdies and blank trials

        # detect location
        if os.path.exists("/Users/shufanzhang/Documents/PhD"):
            self.pictures = [
                self.settings["paths"].get("stimuli_picture_path_laptop")
                + "/"
                + self.settings["stimuli"].get("picture_files")[i]
                for i in range(len(self.settings["stimuli"].get("picture_files")))
            ]
        elif os.path.exists("/home/egter/Projects/arrow_of_time_experiment/aot"):
            self.pictures = [
                self.settings["paths"].get("stimuli_picture_path_sophie")
                + "/"
                + self.settings["stimuli"].get("picture_files")[i]
                for i in range(len(self.settings["stimuli"].get("picture_files")))
            ]

        print(self.pictures)

        # count the time for loading the movies
        start = time.perf_counter()
        # this self.movie_stims is the list that accessed by the trial class by using movie_trial_nr
        self.picture_stims = [
            # use the picture stim class
            ImageStim(
                self.win,
                image=picture,
                size=self.settings["stimuli"].get(
                    "movie_size_pix",
                ),
            )
            for picture in self.pictures  # movie is movie file path name
        ]

        print(
            f"loading {len(self.pictures)} movies took {time.perf_counter()-start} seconds"
        )

    def create_trials(self):
        """Creates trials (ideally before running your session!)"""

        instruction_trial = InstructionTrial(
            session=self,
            trial_nr=0,
            phase_durations=[np.inf],
            txt="Please press buttons to indicate whether you have seen the picture from movies in the session. J for yes, k for no",
            keys=["space"],
        )

        dummy_trial = DummyWaiterTrial(
            session=self,
            trial_nr=1,
            phase_durations=[
                np.inf, self.settings["design"].get("start_duration")],
            txt="Waiting for experiment to start",
        )

        self.trials = [instruction_trial]  # , dummy_trial]
        # self.trials = []

        for picture_trial_nr in range(self.n_trials):
            trial = HCPMovieELTrialMemory(
                session=self,
                trial_nr=picture_trial_nr+2,
                phase_durations=[
                    np.inf,
                ],
                phase_names=["picture"],
                parameters={
                    "picture_index": picture_trial_nr,
                    "picture_file": self.pictures[picture_trial_nr],
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
                    self.output_dir, f"{self.output_str}_memory")
            )

        self.close()


class HCPMovieELSessionGrading(HCPMovieELSession):
    def __init__(
        self,
        output_str: str,
        output_dir: Path,
        core_settings_file: Path,
        run_settings_file: Path,
        eyetracker_on: bool = True,
        training_mode: bool = False,
    ):
        super().__init__(
            output_str,
            output_dir,
            core_settings_file,
            run_settings_file,
            eyetracker_on,
            training_mode,
        )
        self.grades = {}

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
                    "movie_duration": self.settings["stimuli"].get(
                        "experiment_movie_duration"
                    ),
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
    def __init__(
        self,
        output_str: str,
        output_dir: Path,
        core_settings_file: Path,
        run_settings_file: Path,
        eyetracker_on: bool = True,
        training_mode: bool = False,
    ):
        super().__init__(
            output_str,
            output_dir,
            core_settings_file,
            run_settings_file,
            eyetracker_on,
            training_mode,
        )
        self.grades = {}

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
                    "movie_duration": self.settings["stimuli"].get(
                        "experiment_movie_duration"
                    ),
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
