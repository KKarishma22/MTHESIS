import math
import random
from psychopy import core


from constant_utils import to_ms, check_quit, run_iti
from triggers import send_trigger_and_log, trigger_on_flip, pending_resp_end, WAITING_RESP_END
from config import (response_keys, stim_duration, delay_duration, iti_range, hold_required, max_time, ease_power, Cond_code)


def delay(
    win,
    fixation,
    kb,
    duration,
    expected_key,
    exp_clock,
    reset_on_flip=False,
    stim_draw=None,
    stim_duration=0.0,
    trial_clock=None,
    reset_trial_on_flip=False,
    block_start_box=None,
    trial_type=None,
    trigger_ctx=None):
    """
    Starts delay 1 from stimulus onset, or delay 2 from end of response 1. 
    During the delay, tracks whether there are any premature key presses 
    (i.e., before the response period starts) and if so, which key was pressed 
    and whether it was correct based on the expected key for that delay.

    Fixation stays on throughout

    Detects premature presses during delays and:
    - gives feedback by changing fixation colour to red
    - prohibits any pressing during the response period
    
    
    Returns: {"Premature press": bool, "key": str|None, "correct": bool|None}
    """
    
    kb.clearEvents()
    fixation.color = "black"

    timer = core.Clock()
    premature = False
    pressed_key = None
    premature_correct = None

     # Start delay timer exactly at stimulus-onset when requested (i.e., in the case of delay 1))
    if reset_on_flip:
        win.callOnFlip(timer.reset)
        if trial_clock is not None and reset_trial_on_flip:
            win.callOnFlip(trial_clock.reset)

        # trigger for cue onset
        if trigger_ctx is not None:
            trigger_on_flip(
                win=win,
                event_name="cue",
                Cond_code=Cond_code,
                trial_type=trial_type,
                trial_clock=trial_clock,
               **trigger_ctx
            )

        # stamp block start exactly at cue onset flip 
        if block_start_box is not None:
            win.callOnFlip(lambda: block_start_box.__setitem__(0, to_ms(exp_clock)))
    #draw on first frame to ensure timing accuracy of stimulus presentation and delay start
    if stim_draw is not None and stim_duration > 0:
        stim_draw()
    fixation.draw()
    win.flip()
    
    # Loop for the full delay duration
    while timer.getTime() < duration:
        pending_resp_end(kb) # check for resp_end () in case we're in delay 2 and they made a press during response 1 that we're waiting to detect the release of
        check_quit(win, kb)
        t = timer.getTime()

        if not premature:
            presses = kb.getKeys(waitRelease=False, clear=True)
            if presses:
                k = presses[0].name 
                if k != "escape": 
                    premature = True
                    pressed_key = k
                    premature_correct = None if expected_key is None else (k == expected_key)
                    fixation.color = 'red'

        #stimulus drawn only for initial stim_duration ms of the 1st delay period, fixation drawn throughout
        if stim_draw is not None and t < stim_duration:
            stim_draw()
        fixation.draw()
        win.flip()  # fixation stays visible because autoDraw=True
        win.getMovieFrame()
        win.saveMovieFrames("cue.png")
    
    return {"Premature press": premature, "key": pressed_key, "correct": premature_correct}

def run_response_period(
        expected_key,
        win,
        fixation,
        kb,
        vpb_fill,
        vpb_outline,
        trial_clock,
        exp_clock,
        hold_required=hold_required,
        max_time= max_time,
        ease_power= ease_power,
        label= "",
        disabled=False,
        trial_type=None,
        trigger_ctx=None
):
    none_duration = random.uniform(1.300, 1.800)  # random duration for N condition
    kb.clearEvents()
    press_deadline = max_time - hold_required  # the latest time they can make a press and still have time to hold for the required duration

    # initialize result dict with default values; will update based on what happens during the response period and return at the end
    result = {
        "screen_ms": None,        # trial-relative time when response screen first appears
        "rt_ms": None,            # RT relative to response screen onset
        "hold_ms": None,          # measured hold duration (ms)
        "hold_criterion": None,   # 0/1 when response required; None for N
        "criterion_ms": None,    # time (ms) at which hold criterion was met (blank if not met)
        "outcome": None,          # "Hit= 1"/"Miss =0"
        
        #errors
        "error": 0, # general error flag for any incorrect response (e.g., premature or incorrect key press, early release, failure to meet hold criterion within max_time)
        "err_premature_press": 0,
        "err_incorrect_press": 0,
        "err_timeout": 0,
        "err_early_release": 0,
        "err_press_when_none_needed": 0
    }
    # Helper function to log different type of errors made during the response period in the result dict and return it at the end of the response period
    def return_error (result):
        result["error"] = int(
            result["err_premature_press"] == 1 or
            result["err_incorrect_press"] == 1 or
            result["err_timeout"] == 1 or
            result["err_early_release"] == 1 or
            result["err_press_when_none_needed"] == 1
        )
        return result
    # =========================================================
    # NONE CONDITION
    # =========================================================
    # Single response penalty if any error is made
    if expected_key is None:
        kb.clearEvents()

        incorrect = False
        # If delay phase already had a premature press, maintain the red fixation and log as miss
        if disabled and fixation is not None:
            fixation.color = 'red'
        elif fixation is not None:
            fixation.color = 'black'

        n_clock = core.Clock()
        # Stamp screen onset + reset n_clock ON THE SAME FLIP to ensure accurate measurement of response screen onset relative to trial clock and accurate RT measurement relative to response screen onset
        screen_box = [None]
        win.callOnFlip(n_clock.reset)
        win.callOnFlip(lambda: screen_box.__setitem__(0, to_ms(trial_clock.getTime())))

        # Resp_screen trigger sent on same flip as response screen onset for accurate timing relative to trial clock and n_clock
        if trigger_ctx is not None:
            trigger_on_flip(
                win=win,
                event_name="resp_screen1" if label=="Response 1" else "resp_screen2",
                Cond_code=Cond_code,
                trial_type=trial_type,
                trial_clock=trial_clock,
                **trigger_ctx
            )
        vpb_outline.draw()
        win.flip()
        result["screen_ms"] = screen_box[0]

        first_press_t = None
        #first_key = None
        #released = False
        #hold_dur = None

        # Show the box and fixation for non_duration time
        while n_clock.getTime() < none_duration:
            check_quit(win, kb)
        # If press occurs, that's incorrect and penalty follows
            presses = kb.getKeys(waitRelease=False, clear=True)
            if presses and not incorrect:
                k = presses[0].name 
                if k != "escape": 
                    incorrect = True
                    #incorrect_key = k
                    first_press_t = n_clock.getTime()
                    if fixation is not None:
                        fixation.color = 'red'
            #If they made a press, try to detect release so we can log hold duration just for logging purposes
            #if first_key is not None and not released:
            #    ups = kb.getKeys(keyList=[first_key], waitRelease=True, clear=True)
            #    if ups:
            #        released = True
            #        hold_dur = n_clock.getTime() - first_press_t

            if fixation is not None:
                fixation.draw()
            vpb_outline.draw()
            win.flip()
            win.getMovieFrame()
            win.saveMovieFrames("response_period_none.png")
        
            
    
        # outcome rules for N:
        # - if disabled (premature in delay), it's a miss even if no press during N screen
        # - otherwise: no press = 1, press = 0 ("press_when_none" error given)
        if disabled:
            result["outcome"] = 0
            result["err_premature_press"] = 1
            result["hold_criterion"] = math.nan
        elif incorrect:
            result["outcome"] = 0
            result["err_press_when_none_needed"] = 1
            result["rt_ms"] = to_ms(first_press_t) if first_press_t is not None else None   
            #if hold_dur is None:
            #    hold_dur = max(0.0, none_duration - first_press_t)
            #result["hold_ms"] = to_ms(hold_dur) if hold_dur is not None else None
            #result["hold_criterion"] = math.nan
        else:
            result["outcome"] = 1
            result["hold_criterion"] = math.nan
            result["criterion_ms"] = math.nan
        
        if fixation is not None:
            fixation.color = "black"
        return return_error(result)

    # =========================================================
    # DISABLED (PREMATURE PRESS IN DELAY)
    # =========================================================
    # Premature presses DESERVE A PENALTY HAHA : empty outline only, fixation red, ignore subsequent key presses
    if disabled:
        if fixation is not None:
            fixation.color = 'red'
        
        kb.clearEvents()
        # Stamp response screen onset for triggers and logging
        penalty_clock = core.Clock()
        screen_box = [None]

        win.callOnFlip(penalty_clock.reset)
        win.callOnFlip(lambda: screen_box.__setitem__(0, to_ms(trial_clock.getTime())))
        
        if trigger_ctx is not None:
            trigger_on_flip(
                win=win,
                event_name="resp_screen1" if label=="Response 1" else "resp_screen2",
                Cond_code=Cond_code,
                trial_type=trial_type,
                trial_clock=trial_clock,
                **trigger_ctx
            )
        # first presentation of response screen
        if fixation is not None:
            fixation.draw()
        vpb_outline.draw()
        win.flip()
        result["screen_ms"] = screen_box[0]
        
        # penalty: show frozen bar and red fixation for the full max_duration, ignore any attempts to rectify
        while penalty_clock.getTime() < max_time:
            check_quit(win, kb)
            kb.clearEvents()
            if fixation is not None:
                fixation.draw()
            vpb_outline.draw()
            win.flip()
            win.getMovieFrame()
            win.saveMovieFrames("penalty1.png")
        
        if fixation is not None:
            fixation.color = 'black'  # reset fixation color after penalty
        # Log error
        result["outcome"] = 0
        result["err_premature_press"] = 1
        result["hold_criterion"] = math.nan
        result["criterion_ms"] = math.nan
        return return_error(result)
    
    # =========================================================
    # WHEN A RESPONSE IS REQUIRED
    # =========================================================

    # --- filling the bar inside ---
    lw = getattr(vpb_outline, "lineWidth", 0) or 0
    inner_h = vpb_outline.height - 2 * lw    #to ensure fill fits inside outline not overlapping it
    bottom_y = (vpb_outline.pos[1] - vpb_outline.height / 2) + lw
    x = vpb_outline.pos[0]

    # reset bar to empty at start
    vpb_fill.height = 0
    vpb_fill.pos = (x, bottom_y)

    # --- clocks for normal response, early release, timeouts ---
    start_clock = core.Clock() # for max_time (2 seconds wherein a person can make a response) and RT
    hold_clock = core.Clock()  # for hold duration
    freeze_clock = core.Clock() # for stop after early release

    holding_started = False   #track whether a key press has occurred/started
    rt = None                 # if yes, store the reaction time (time of first key press)
    missed_deadline = False # track whether they missed the initial deadline to start pressing (i.e., pressed after 1 second and thus didn't have time to hold for a full second)

    # Stamp response screen onset + reset start_clock exactly at first response-screen flip
    screen_box = [None]
    win.callOnFlip(start_clock.reset)
    win.callOnFlip(lambda: screen_box.__setitem__(0, to_ms(trial_clock.getTime())))

    # Trigger for response screen onset
    if trigger_ctx is not None:
        trigger_on_flip(
            win=win,
            event_name="resp_screen1" if label=="Response 1" else "resp_screen2",
            Cond_code=Cond_code,
            trial_type=trial_type,
            trial_clock=trial_clock,
            **trigger_ctx
        )

    # first presentation of response screen (same visuals as your loop)
    vpb_fill.draw()
    vpb_outline.draw()
    win.flip()
    result["screen_ms"] = screen_box[0]

    # =========================================================
    # WAIT FOR INITIAL PRESS
    # =========================================================
    # Loop until key press or until max_time has passed
    while start_clock.getTime() < max_time:
        check_quit(win,kb)
        # Timeout penalty
        if not holding_started and start_clock.getTime() >= press_deadline:
            missed_deadline = True
            if fixation is not None:
                fixation.color = 'red'  # indicate missed deadline with red fixation
        # Time out penalty
        if missed_deadline:
            kb.clearEvents()  # ignore any key presses after missed deadline
            if fixation is not None:
                fixation.draw()
            vpb_outline.draw() #draw an empty outline to show the missed response
            win.flip()
            win.getMovieFrame()
            win.saveMovieFrames("missed_deadline.png")
            continue
        # Correct press starts the hold period
        presses = kb.getKeys (waitRelease=False, clear=True)
        if presses:
            k = presses[0].name
            if k==expected_key:
                holding_started = True
                rt = start_clock.getTime()

                #trigger for response start
                if trigger_ctx is not None:
                    send_trigger_and_log(
                        event_name="resp1_start" if label=="Response 1" else "resp2_start",
                        Cond_code=Cond_code,
                        trial_type=trial_type,
                        trial_clock=trial_clock,
                        **trigger_ctx
                    )
                hold_clock.reset()  # start hold clock on first press of expected key
                break
            # Incorrect press leads to penalty by showing red fixation and ignoring subsequent presses for the rest of the response period
            elif k != "escape":
                result["outcome"] = 0
                result["err_incorrect_press"] = 1
                result["hold_criterion"] = 0

                if fixation:
                    fixation.color = "red"

                while start_clock.getTime() < max_time:
                    check_quit(win, kb)
                    kb.clearEvents()
                    if fixation:
                        fixation.draw()
                    vpb_outline.draw()
                    win.flip()

                if fixation:
                    fixation.color = "black"

                return return_error(result)

        vpb_fill.draw()
        vpb_outline.draw()
        win.flip()
        

    # Error logging for missed deadline
    if missed_deadline:
        if fixation is not None:
            fixation.color = 'black'
            result["outcome"] = 0
            result["err_timeout"] = 1
            result["hold_criterion"] = 0
            result["criterion_ms"] = math.nan
            return return_error(result)
    
    result["rt_ms"] = to_ms(rt) if rt is not None else None


    released_early = False
    frozen_height = 0.0
    remaining_time = 0.0
    hold_measured = None
    
  
    while True:
        pending_resp_end(kb)
        check_quit(win, kb)

        if not released_early:
            elapsed = hold_clock.getTime()

            # update fill based on elapsed hold time
            progress = min(1.0, elapsed / hold_required)
            visual_progress = progress ** ease_power
            bar_h = visual_progress * inner_h 

            vpb_fill.height = bar_h
            vpb_fill.pos = (x, bottom_y + bar_h / 2)

        # -------------------------------
        # SUCCESSFUL HOLD
        # -------------------------------
            if elapsed >= hold_required:
                hold_measured = elapsed
                
                # draw full bar once
                vpb_fill.height = inner_h
                vpb_fill.pos = (x, bottom_y + inner_h / 2)
                vpb_fill.draw()
                vpb_outline.draw()
                win.flip()
                win.getMovieFrame()
                win.saveMovieFrames("success.png")

                # waits for key release to send resp_end trigger
                if trigger_ctx is not None:
                    WAITING_RESP_END["waiting_release"] = True
                    WAITING_RESP_END["key"] = expected_key

                    def on_release():
                        send_trigger_and_log(
                            event_name="resp1_end" if label=="Response 1" else "resp2_end",
                            Cond_code=Cond_code,
                            trial_type=trial_type,
                            trial_clock=trial_clock,
                            **trigger_ctx
                        )

                    WAITING_RESP_END["on_release"] = on_release
                pending_resp_end(kb) # in case they released the key on the same frame as meeting the hold criterion, check for it now so we can send the trigger immediately instead of waiting for another key event
                result["outcome"] = 1
                result["hold_ms"] = to_ms(hold_measured) if hold_measured is not None else None
                result["hold_criterion"] = 1
                result["criterion_ms"] = to_ms(rt + hold_required)  #when the one second hold criterion was met relative to response screen onset

                return return_error(result)

            # -------------------------------
            # EARLY RELEASE
            # -------------------------------
            ups = kb.getKeys(keyList=[expected_key], waitRelease=True, clear=True)
            if ups:
                if trigger_ctx is not None:
                    send_trigger_and_log(
                        event_name="resp1_end" if label=="Response 1" else "resp2_end",
                        Cond_code=Cond_code,
                        trial_type=trial_type,
                        trial_clock=trial_clock,
                        **trigger_ctx
                    )
                released_early = True
                hold_measured = elapsed
                frozen_height = vpb_fill.height
                remaining_time = max(0.0, hold_required - elapsed)
                freeze_clock.reset()
                kb.clearEvents()
                if fixation is not None:
                    fixation.color = 'red'  # indicate early release with red fixation

        else:
            kb.clearEvents()
            # Freeze bar at release height
            vpb_fill.height = frozen_height
            vpb_fill.pos = (x, bottom_y + frozen_height / 2)
            if freeze_clock.getTime() >= remaining_time:
                vpb_fill.draw()
                vpb_outline.draw()
                if fixation is not None:
                    fixation.color = "black"
                win.flip()
                win.getMovieFrame()
                win.saveMovieFrames("early_release.png")

                result["outcome"] = 0
                result["err_early_release"] = 1
                result["hold_ms"] = to_ms(hold_measured) if hold_measured is not None else None
                result["hold_criterion"] = 0
                result["criterion_ms"] = math.nan
                return return_error(result)
        vpb_fill.draw()
        vpb_outline.draw()
        win.flip()

def run_trial(
    trial_type,
    block_num,
    trial_in_block,
    block_start_ms,
    global_trial,
    win,
    fixation,
    kb,
    exp_clock,
    stim_top,
    stim_bottom,
    vpb_fill,
    vpb_outline,
    trigger_ctx
):
    first_resp, second_resp = trial_type.split(" - ")
    check_quit(win, kb)
     # expected keys
    expected1 = response_keys[first_resp]                 # always x/m
    expected2 = response_keys.get(second_resp, None)      # x/m or None (N)

    # trial clock: will be reset to 0 exactly on the cue-onset flip
    trial_clock = core.Clock()
    
    # 1) stimulus + delay 1
    stim_top.text = first_resp
    stim_bottom.text = second_resp

    def stim_draw():
        stim_top.draw()
        stim_bottom.draw()
    
    block_start_box = None
    if trial_in_block == 1 and block_start_ms is None:
        block_start_box = [None]

    prem1 = delay(
        win=win, fixation=fixation, kb=kb, exp_clock=exp_clock,
        duration= stim_duration + delay_duration,
        expected_key=expected1,
        reset_on_flip=True,  # ensure delay timer starts at stimulus onset
        stim_draw=stim_draw,
        stim_duration=stim_duration,
        trial_clock=trial_clock,
        reset_trial_on_flip=True,  # ensure trial-relative timings are accurate starting from cue onset
        block_start_box=block_start_box,
        trial_type=trial_type,
        trigger_ctx=trigger_ctx
  )
    if block_start_ms is None and block_start_box is not None:
        block_start_ms = block_start_box[0]

    #cue onset is trial start
    cue_onset_ms = 0 

    # 3) response 1
    if first_resp in response_keys:
        check_quit(win, kb)
        R1 = run_response_period(
            expected_key=expected1,
            win=win, vpb_fill=vpb_fill, vpb_outline=vpb_outline,fixation=fixation, exp_clock=exp_clock,
            kb=kb, trial_clock=trial_clock, hold_required=hold_required, max_time=max_time, ease_power=ease_power,
            label="Response 1",  
            disabled = prem1["Premature press"], 
            trial_type=trial_type,
            trigger_ctx=trigger_ctx  
        )
        pending_resp_end(kb)
    # 4) delay 2
    
    prem2 = delay(
        win=win, fixation=fixation, kb=kb, duration=delay_duration, 
        expected_key=expected2, block_start_box=block_start_box,
        exp_clock=exp_clock, trial_clock=trial_clock,
        trial_type=trial_type, 
        trigger_ctx=trigger_ctx)

    # 5) response 2 
   
    R2 = run_response_period(
        expected_key=expected2,
        win=win,
        fixation=fixation,
        kb=kb,
        vpb_fill=vpb_fill,
        vpb_outline=vpb_outline,
        trial_clock=trial_clock,
        exp_clock=exp_clock,
        hold_required=hold_required,
        max_time=max_time,
        ease_power=ease_power,
        label="Response 2",
        disabled=prem2["Premature press"],
        trial_type=trial_type,
        trigger_ctx=trigger_ctx  
        )

    pending_resp_end(kb)
    win.flip()
    # 6) ITI jitter
    iti_duration = random.uniform(*iti_range)
    iti_info = run_iti(
        win=win, 
        kb=kb, 
        duration=iti_duration, 
        fixation=fixation
    )

    if R1["outcome"] == 1 and R2["outcome"] == 1:
        trial_use = 1  #1= use
    else:
        trial_use = 0  #0= No use
     # ---- build row (keys MUST match TRIAL_FIELDS exactly) ----
    row = {
        #"Study_ID": study_id if write_session_info else "",
        #"Subject_ID": subjID if write_session_info else "",
        #"Date": date_str if write_session_info else "",
        #"Session_start": session_start  if write_session_info else "",
        
        "Block": block_num,
        "Block_start_ms": block_start_ms,  # relative to experiment start
        "Trial": trial_in_block,
        "Trial_global": global_trial,
        "Cond_code": Cond_code[trial_type],
        "Trial_use": trial_use,

        # trial-relative: cue onset is the trial start, so 0
        "cue_onset_ms": 0,

        "R1_screen_ms": R1["screen_ms"] if R1["screen_ms"] is not None else math.nan,
        "R1_rt_ms": R1["rt_ms"] if R1["rt_ms"] is not None else math.nan,
        "R1_hold_ms": R1["hold_ms"] if R1["hold_ms"] is not None else math.nan,
        "R1_hold_criterion": R1["hold_criterion"] if R1["hold_criterion"] is not None else math.nan,
        "R1_criterion_ms": R1["criterion_ms"] if R1["criterion_ms"] is not None else math.nan,
        "R1_outcome": R1["outcome"] if R1["outcome"] is not None else math.nan,
        "R1_error": R1["error"],
        "R1_err_premature_press": R1["err_premature_press"], 
        "R1_err_incorrect_press": R1["err_incorrect_press"], 
        "R1_err_timeout": R1["err_timeout"], 
        "R1_err_early_release": R1["err_early_release"], 

        "R2_screen_ms": R2["screen_ms"] if R2["screen_ms"] is not None else math.nan,
        "R2_rt_ms": R2["rt_ms"] if R2["rt_ms"] is not None else math.nan,
        "R2_hold_ms": R2["hold_ms"] if R2["hold_ms"] is not None else math.nan,
        "R2_hold_criterion": R2["hold_criterion"] if R2["hold_criterion"] is not None else math.nan,
        "R2_criterion_ms": R2["criterion_ms"] if R2["criterion_ms"] is not None else math.nan,
        "R2_outcome": R2["outcome"] if R2["outcome"] is not None else math.nan,
        "R2_error": R2["error"],
        "R2_err_premature_press": R2["err_premature_press"], 
        "R2_err_incorrect_press": R2["err_incorrect_press"], 
        "R2_err_timeout": R2["err_timeout"], 
        "R2_err_early_release": R2["err_early_release"],
        "R2_err_press_when_none_needed": R2["err_press_when_none_needed"],

        # ITI columns (only if you add them to TRIAL_FIELDS)
        "ITI_duration_ms": int(round(iti_duration * 1000)),
        "ITI_n": iti_info["iti_n"],
        "ITI_keypress": iti_info["iti_keypress"] if iti_info["iti_keypress"] is not None else math.nan,
        "ITI_keypresstime": iti_info["iti_keypresstime"] if iti_info["iti_keypresstime"] is not None else math.nan,
    }

    return row