"""
To create different stimuli (fixation, cues, response bar)

"""

from psychopy import visual

class Stimuli:
    def __init__(self, win):

        self.fixation = visual.TextStim (win, text="+", color='black', pos=(0, 0), height=40, bold= False)
        self.stim_top = visual.TextStim(win, text="", color='black', height=30, pos=(0, 40), bold=False)
        self.stim_bottom = visual.TextStim(win, text="", color='black', height=30, pos=(0, -40), bold=False)
        self.message_stim = visual.TextStim(win, text="", color='black', height=28, wrapWidth=1000)
        self.vpb_outline = visual.Rect( win, width=65, height=220, lineColor='black', fillColor=None, lineWidth=3, pos=(0, 0))
        self.vpb_fill = visual.Rect( win, width=60, height=0, fillColor='gray', lineColor=None, pos=(0, 0))
