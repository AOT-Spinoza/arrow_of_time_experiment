import numpy as np
from exptools2.core import Trial
from psychopy.visual import TextStim
from stimuli import FixationLines
import warnings

try:
    import pylink
except ModuleNotFoundError:
    msg = "Pylink is not installed! Eyetracker cannot be used"
    warnings.warn(msg)
    PYLINK_AVAILABLE = False
else:
    PYLINK_AVAILABLE = True


class HCPMovieELTrial(Trial):
    def __init__(
        self,
        session,
        trial_nr,
        phase_durations,
        phase_names,
        parameters,
        timing="seconds",
        verbose=True,
    ):
        """Initializes a StroopTrial object.

        Parameters
        ----------
        session : exptools Session object
            A Session object (needed for metadata)
        trial_nr: int
            Trial nr of trial
        phase_durations : array-like
            List/tuple/array with phase durations
        phase_names : array-like
            List/tuple/array with names for phases (only for logging),
            optional (if None, all are named 'stim')
        parameters : dict
            Dict of parameters that needs to be added to the log of this trial
        timing : str
            The "units" of the phase durations. Default is 'seconds', where we
            assume the phase-durations are in seconds. The other option is
            'frames', where the phase-"duration" refers to the number of frames.
        verbose : bool
            Whether to print extra output (mostly timing info)
        """
        super().__init__(
            session,
            trial_nr,
            phase_durations,
            phase_names,
            parameters,
            timing,
            load_next_during_phase=None,
            verbose=verbose,
        )

    def create_trial(self):
        pass

    def draw(self):
        #self.session.fixation.draw()
        if self.phase == 1:
            self.session.movie_stims[self.parameters["movie_index"]].draw()
            #self.session.fixation.draw()


class HCPMovieELTrialGrading(Trial):
    def __init__(
        self,
        session,
        trial_nr,
        phase_durations,
        phase_names,
        parameters,
        timing="seconds",
        verbose=True,
    ):
        """Initializes a StroopTrial object.

        Parameters
        ----------
        session : exptools Session object
            A Session object (needed for metadata)
        trial_nr: int
            Trial nr of trial
        phase_durations : array-like
            List/tuple/array with phase durations
        phase_names : array-like
            List/tuple/array with names for phases (only for logging),
            optional (if None, all are named 'stim')
        parameters : dict
            Dict of parameters that needs to be added to the log of this trial
        timing : str
            The "units" of the phase durations. Default is 'seconds', where we
            assume the phase-durations are in seconds. The other option is
            'frames', where the phase-"duration" refers to the number of frames.
        verbose : bool
            Whether to print extra output (mostly timing info)
        """
        super().__init__(
            session,
            trial_nr,
            phase_durations,
            phase_names,
            parameters,
            timing,
            load_next_during_phase=None,
            verbose=verbose,
        )

    def create_trial(self):
        pass

    def draw(self):
        #self.session.fixation.draw()
        if self.phase == 1:
            self.session.movie_stims[self.parameters["movie_index"]].draw()
            #self.session.fixation.draw()

    def get_events(self):  # record grading of movie
        # trail waiting for events to stop
        events = Trial.get_events(self)
        if events:
            for key, t in events:
                if key == "J" or key == "j":
                    self.session.grades[self.parameters["movie_file"]] = key
                    # self.session.grades.append((self.parameters['movie_file'], key))
                    self.stop_phase()
                elif key == "K" or key == "k":
                    self.session.grades[self.parameters["movie_file"]] = key
                    # self.session.grades.append((self.parameters['movie_file'], key))
                    self.stop_phase()
                if key == "L" or key == "l":
                    self.session.grades[self.parameters["movie_file"]] = key
                    # self.session.grades.append((self.parameters['movie_file'], key))
                    self.stop_phase()
                elif key == ":" or key == ";":
                    self.session.grades[self.parameters["movie_file"]] = key
                    # self.session.grades.append((self.parameters['movie_file'], key))
                    self.stop_phase()


class HCPMovieELTrialLabeling(Trial):
    def __init__(
        self,
        session,
        trial_nr,
        phase_durations,
        parameters,
        phase_names=None,
        timing="seconds",
        verbose=True,
    ):
        """Initializes a StroopTrial object.

        Parameters
        ----------
        session : exptools Session object
            A Session object (needed for metadata)
        trial_nr: int
            Trial nr of trial
        phase_durations : array-like
            List/tuple/array with phase durations
        phase_names : array-like
            List/tuple/array with names for phases (only for logging),
            optional (if None, all are named 'stim')
        parameters : dict
            Dict of parameters that needs to be added to the log of this trial
        timing : str
            The "units" of the phase durations. Default is 'seconds', where we
            assume the phase-durations are in seconds. The other option is
            'frames', where the phase-"duration" refers to the number of frames.
        verbose : bool
            Whether to print extra output (mostly timing info)
        """
        super().__init__(
            session,
            trial_nr,
            phase_durations,
            phase_names,
            parameters,
            timing,
            load_next_during_phase=None,
            verbose=verbose,
        )
        txt_height = self.session.settings["various"].get("text_height")
        txt_width = self.session.settings["various"].get("text_width")
        self.text_list = self.session.settings["various"].get("text_list")
        self.text_stims = []
        for text in self.text_list:
            self.text_stims.append(
                TextStim(
                    self.session.win,
                    text=text,
                    height=txt_height,
                    wrapWidth=txt_width,
                    color="white",
                )
            )
        if phase_names is None:
            phase_names = ["stim"]

    def create_trial(self):
        pass

    def draw(self):
        #self.session.fixation.draw()
        if self.phase == 1:
            self.session.movie_stims[self.parameters["movie_index"]].draw()
            self.session.grades[self.parameters["movie_file"]] = {}
            self.session.fixation.draw()
        phase_length = len(self.phase_durations)
        for phase in range(2, phase_length + 1):
            if self.phase == phase:
                self.text_stims[phase - 2].draw()
                #self.session.fixation.draw()

    def get_events(
        self,
    ):  # record grading of movie #每个视频下面又有一个dict，里面是每个phase/text的评分 改grade记录 phase time随着信号结束  视频源
        # trail waiting for events to stop
        events = Trial.get_events(self)
        if events:
            label_index = self.phase - 2
            label = self.text_list[label_index]
            for key, t in events:
                if key == "J" or key == "j":
                    self.session.grades[self.parameters["movie_file"]][label] = key
                    # self.session.grades.append((self.parameters['movie_file'], key))
                    self.stop_phase()
                elif key == "K" or key == "k":
                    self.session.grades[self.parameters["movie_file"]][label] = key
                    # self.session.grades.append((self.parameters['movie_file'], key))
                    self.stop_phase()
                if key == "L" or key == "l":
                    self.session.grades[self.parameters["movie_file"]][label] = key
                    # self.session.grades.append((self.parameters['movie_file'], key))
                    self.stop_phase()
                elif key == ":" or key == ";":
                    self.session.grades[self.parameters["movie_file"]][label] = key
                    # self.session.grades.append((self.parameters['movie_file'], key))
                    self.stop_phase()


class InstructionTrial(Trial):
    """Simple trial with instruction text."""

    def __init__(
        self, session, trial_nr, phase_durations=[np.inf], txt=None, keys=None, **kwargs
    ):

        super().__init__(session, trial_nr, phase_durations, **kwargs)

        txt_height = self.session.settings["various"].get("text_height")
        txt_width = self.session.settings["various"].get("text_width")

        if txt is None:
            txt = """Press any button to continue."""

        self.text = TextStim(
            self.session.win, txt, height=txt_height, wrapWidth=txt_width, **kwargs
        )

        self.keys = keys

    def draw(self):
        self.session.fixation.draw()
        self.session.report_fixation.draw()

        self.text.draw()

    def get_events(self):
        events = super().get_events()

        if self.keys is None:
            if events:
                self.stop_phase()
        else:
            for key, t in events:
                if key in self.keys:
                    self.stop_phase()


class DummyWaiterTrial(InstructionTrial):
    """Simple trial with text (trial x) and fixation."""

    def __init__(
        self,
        session,
        trial_nr,
        phase_durations=None,
        txt="Waiting for scanner triggers.",
        **kwargs
    ):

        super().__init__(session, trial_nr, phase_durations, txt, **kwargs)

    def draw(self):
        self.session.fixation.draw()
        if self.phase == 0:
            self.text.draw()
        else:
            self.session.report_fixation.draw()

    def get_events(self):
        events = Trial.get_events(self)

        if events:
            for key, t in events:
                if key == self.session.mri_trigger:
                    if self.phase == 0:
                        self.stop_phase()


class OutroTrial(InstructionTrial):
    """Simple trial with only fixation cross."""

    def __init__(self, session, trial_nr, phase_durations, txt="", **kwargs):

        txt = """"""
        super().__init__(session, trial_nr, phase_durations, txt=txt, **kwargs)

    def get_events(self):
        events = Trial.get_events(self)

        if events:
            for key, t in events:
                if key == "space":
                    self.stop_phase()
