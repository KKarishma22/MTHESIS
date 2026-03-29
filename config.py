"""
All configuration for the experiment.
"""
import random

study_id = "ActionPlanExec"
# Trial and block structure
blocks = 2       #whatever number of blocks we want
trials_per_block = 6 #whatever number of trials per block we want
trial_types = ["L - L", "L - R", "R - L", "R - R", "R - N", "L - N"]

# Timings 
stim_duration = .500 
delay_duration = 1.500
iti_range = (0.500, 1.000)
hold_required= 1.000
max_time = 2.000
ease_power = 2.0

# Response keys
response_keys = {'L': 'x', 'R': 'm'}

# Messages
messages = {
    "CALIBRATION":(
    "Eyetracker calibration...\n\n"
    ),
    
    "calibration_question": (
    "Start eyetracker calibration?"
    ),

    "start": (
        "Welcome to our study!\n\n"
        "You will see two letters (a combination of L/R/N) above and below a fixation cross (+) indicating which hand to use to make a response.\n\n"
        "L--> left hand response, R--> right hand response, N--> no response needed, do not press anything\n\n"
        "Press 'x' key for making a LEFT hand response and 'm' for a RIGHT hand response.\n\n"
        "To make a successful response press and hold the key down until the rectangular bar is filled to the top and the trial moves forward.\n\n"
        "Press any key to begin."
    ),
    "block_start": (
        "Starting block {block_num} of {total_blocks}.\n\n"
        "Press any key to continue."
    ),
    "block_end": (
        "You have completed block {block_num} of {total_blocks}.\n\n"
        "Press any key to continue when you're ready."
    ),
    "halfway": (
        "You are halfway through the experiment.\n"
        "Take a short break if needed.\n\n"
        "Press any key to continue."
    ),
    "end": (
        "The experiment is complete.\n"
        "Thank you for your participation!\n\n"
        "Press any key to exit."
    ),
}

Cond_code = {
    "L - L": 1,
    "L - R": 2,
    "L - N": 3,
    "R - R": 4,
    "R - L": 5,
    "R - N": 6
}

TRIAL_FIELDS = [
    #"Study_ID", "Subject_ID", "Date",
    #"Session_start", 
    
    # block/trial info
    "Block",                 # e.g., "1/4"
    "Block_start_ms",        # relative to exp start
    "Trial",                 # e.g., "1/60"
    "Trial_global",
    "Cond_code",        # 1..6
    "Trial_use",      # use/ no_use

    #Timings( in ms relative to trial (cue_onset) start)
    "cue_onset_ms",
    "R1_screen_ms",
    "R1_rt_ms",
    "R1_hold_ms",            # how long press was held
    "R1_hold_criterion",       # 0/1
    "R1_criterion_ms",        # time (ms) at which hold criterion was met (blank if not met)
    "R1_outcome",            # "Hit= 1"/"Miss =0"
    
    "R1_error",              # was there an error made? 0/1 
    "R1_err_premature_press",     # 0/1
    "R1_err_incorrect_press",     # 0/1
    "R1_err_early_release",        # 0/1
    "R1_err_timeout",            # 0/1
                              

    "R2_screen_ms",
    "R2_rt_ms",
    "R2_hold_ms",
    "R2_hold_criterion",# 0/1 ("NaN" for N)
    "R2_criterion_ms",
    "R2_outcome",

    "R2_error", # was there an error made? 0/1
    "R2_err_premature_press", #0/1
    "R2_err_incorrect_press", #0/1
    "R2_err_timeout", #0/1
    "R2_err_early_release", #0/1
    "R2_err_press_when_none_needed", #0/1


    "ITI_duration_ms",
    "ITI_n",
    "ITI_keypress",
    "ITI_keypresstime",
]

demographics_fields = [
    "Study_ID","Subject_ID","Date",
    "Session_start", "Session_end", "Status",
    "Age","Gender","Handedness","Vision",
]

EVENT_OFFSET= {
    "cue" : 10,
    "resp_screen1" : 20,
    "resp1_start" : 30,
    "resp1_end" : 40,
    "resp_screen2" : 50,
    "resp2_start" : 60,
    "resp2_end" : 70,
}
TRIGGER_FIELDS = [
    "Block", "Trial", "Trial_global", "Cond_code",
    "Event", "Trigger_code", "exp_ms", "trial_ms",
]
