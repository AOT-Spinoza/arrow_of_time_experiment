import numpy as np
from psychopy.visual import TextStim, Line, RadialStim,Circle,DotStim,GratingStim
import warnings


class FixationLines(object):

    def __init__(self, win, circle_radius, color, line_width, *args, **kwargs):
        self.color = color
        self.line_width = line_width 
        self.line1 = Line(win, start=(-circle_radius, -circle_radius),
                          end=(circle_radius, circle_radius), lineColor=self.color, lineWidth=self.line_width, *args, **kwargs)
        self.line2 = Line(win, start=(-circle_radius, circle_radius),
                          end=(circle_radius, -circle_radius), lineColor=self.color, lineWidth=self.line_width, *args, **kwargs)

    def draw(self):
        self.line1.draw()
        self.line2.draw()

    def setColor(self, color):
        self.line1.color = color
        self.line2.color = color
        self.color = color

#fixation cross with dot in the middle
class FixationLine2(object):
    
        def __init__(self, win, circle_radius, color, line_width, *args, **kwargs):
            self.color = color
            self.line_width = line_width
            self.line1 = Line(win, start=(-circle_radius, -circle_radius),
                            end=(circle_radius, circle_radius), lineColor=self.color, lineWidth=self.line_width, *args, **kwargs)
            self.line2 = Line(win, start=(-circle_radius, circle_radius),
                            end=(circle_radius, -circle_radius), lineColor=self.color, lineWidth=self.line_width, *args, **kwargs)

            self.dot = DotStim(win, color=self.color, *args, **kwargs)
    
        def draw(self):
            self.line1.draw()
            self.line2.draw()
            self.dot.draw()
    
        def setColor(self, color):
            self.line1.color = color
            self.line2.color = color
            self.dot.color = color
            self.color = color
    


class FixationBullsEye(object):

    def __init__(self, win, circle_radius, color, pos=[0,0], edges=360, *args, **kwargs):
        self.color = color
        self.line1 = Line(win, start=(-circle_radius+pos[0], -circle_radius+pos[1]),
                          end=(circle_radius+pos[0], circle_radius+pos[1]), lineColor=self.color, *args, **kwargs)
        self.line2 = Line(win, start=(-circle_radius+pos[0], circle_radius+pos[1]),
                          end=(circle_radius+pos[0], -circle_radius+pos[1]), lineColor=self.color, *args, **kwargs)
        #self.circle1 = Circle(win, radius=circle_radius*0.1, edges=edges, fillColor=None, lineColor=self.color, *args, **kwargs)
        self.circle2 = Circle(win, radius=circle_radius*0.01, edges=edges, fillColor=(-1,-1,-1), lineColor=self.color, *args, **kwargs)
        #self.circle3 = Circle(win, radius=circle_radius*0.25, edges=edges, fillColor=None, lineColor=self.color, *args, **kwargs)
        #self.circle4 = Circle(win, radius=circle_radius*0.125, edges=edges, fillColor=None, lineColor=self.color, *args, **kwargs)
        self.surround_fixation_dot = GratingStim(
            win,
            size=circle_radius*0.02,
            contrast=0,
            mask='raisedCos',
            maskParams={'fringeWidth': circle_radius*0.4})

    def draw(self):
        self.surround_fixation_dot.draw()
        self.circle2.draw()
        self.line1.draw()
        self.line2.draw()
        #self.circle1.draw()
        
        #self.circle3.draw()
        #self.circle4.draw()

    def setColor(self, color):
        self.line1.color = color
        self.line2.color = color
        #self.circle1.color = color
        self.circle2.color = color
        #self.circle3.color = color
        #self.circle4.color = color
        self.color = color


        
