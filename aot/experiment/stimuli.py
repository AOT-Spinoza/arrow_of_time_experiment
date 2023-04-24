import numpy as np
from psychopy.visual import TextStim, Line, RadialStim, Circle, DotStim, GratingStim
import warnings


class FixationBullsEye(object):
    def __init__(
        self, win, outer_radius, line_color, line_width=None, pos=[0, 0], dot_size=None, dot_color=None, dot_perimeter_size=None, dot_perimeter_smoothness=0.4, edges=180, *args, **kwargs
    ):
        self.pos = pos
        self.line_color = line_color
        self.line_width = line_width
        self.dot_color = dot_color
        self.dot_perimeter_size = dot_perimeter_size
        self.dot_size = dot_size
        self.dot_perimeter_smoothness = dot_perimeter_smoothness
        self.edges = edges

        self.line1 = Line(
            win,
            start=(-outer_radius + self.pos[0], -outer_radius + self.pos[1]),
            end=(outer_radius + self.pos[0], outer_radius + self.pos[1]),
            lineColor=self.line_color,
            lineWidth=self.line_width,
            *args,
            **kwargs
        )
        self.line2 = Line(
            win,
            start=(-outer_radius + self.pos[0], outer_radius + self.pos[1]),
            end=(outer_radius + self.pos[0], -outer_radius + self.pos[1]),
            lineColor=self.line_color,
            lineWidth=self.line_width,
            *args,
            **kwargs
        )
        self.circle = Circle(
            win,
            pos=self.pos,
            radius=self.dot_size,
            edges=edges,
            fillColor=self.dot_color,
            lineColor=self.line_color,
            lineWidth=self.line_width,
            *args,
            **kwargs
        )

        self.surround_fixation_dot = GratingStim(
            win,
            pos=self.pos,
            size=self.dot_perimeter_size,
            contrast=0,
            mask="raisedCos",
            maskParams={"fringeWidth": self.dot_perimeter_smoothness},
        )

    def draw(self):
        self.surround_fixation_dot.draw()
        self.circle.draw()
        self.line1.draw()
        self.line2.draw()

