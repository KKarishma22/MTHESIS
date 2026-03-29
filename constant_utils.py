from psychopy import core, event
import random
import logging
from triggers import pending_resp_end

# ====================== QUIT HANDLING ====================== #
#quit_requested = False
#def request_quit()
#    global quit_requested
#    quit_requested = True
def check_quit(win, kb):
    if kb.getKeys(['escape'], waitRelease=False):
        print("Experiment ended")
        win.close()
        core.quit()
        
#def check_quit():
#    if quit_requested:
#        print("Experiment ended")
#        win.close()
#        core.quit()
#        raise SystemExit

#event.globalKeys.clear()
#event.globalKeys.add(key='escape', func=request_quit)
# ====================== FUNCTIONS ====================== #
# Clock and timing
def to_ms(clock_or_sec, sec=None):
    """
    Convert seconds -> integer milliseconds.

    Accepts either:
      - a PsychoPy Clock-like object (has .getTime()), OR
      - a numeric seconds value, OR
      - a Timestamp-like object.
    """
    if sec is None:
        x = clock_or_sec

        # If it's a Clock, get the time first
        if hasattr(x, "getTime"):
            x = x.getTime()

        # PsychoPy Timestamp often exposes .time
        if hasattr(x, "time"):
            x = x.time
        # Pandas Timestamp exposes .timestamp()
        elif hasattr(x, "timestamp") and callable(getattr(x, "timestamp")):
            x = x.timestamp()

        return int(round(float(x) * 1000))

    x = sec
    if hasattr(x, "time"):
        x = x.time
    elif hasattr(x, "timestamp") and callable(getattr(x, "timestamp")):
        x = x.timestamp()
    return int(round(float(x) * 1000))


def clock_ms(clock):
    """For trial-relative timings."""
    t = clock.getTime()
    if hasattr(t, "time"):
        t = t.time
    elif hasattr(t, "timestamp") and callable(getattr(t, "timestamp")):
        t = t.timestamp()
    return int(round(float(t) * 1000))

# Showing messages
def show_message(win, message_stim, fixation, 
                 kb, text, wait=True, allow_escape=False, 
                 allow_et_setup=False, eye_tracker=None, ET=False, 
                 require_confirm=False, et_keys=("c","v")):
    """
    Message screen with optional:
      - press 'c' -> enter setup and (try to) start calibration
      - press 'v' -> enter setup and (try to) start validation
    Only active if allow_et_setup=True AND ET=True AND eye_tracker is not None.
    Esc works

    After leaving EyeLink setup (ESC inside EyeLink UI), returns to the SAME
    message screen and waits again. Any other key continues.
    """
    fixation.autoDraw = False # hide fixation during messages
    message_stim.text = text
    message_stim.draw()
    win.flip()

    if not wait:
        return[]
    event.clearEvents()
    kb.clearEvents()
    while True:
        # Always poll for pending key-release triggers
        pending_resp_end(kb)

        # Check for Escape every frame when not in allow_escape mode
        if not allow_escape:
            check_quit(win, kb)

        keys = event.getKeys()
        if not keys:
            continue

        k = keys[0].lower()

        # ---------- EyeLink calibration / validation hotkeys ----------
        if allow_et_setup and ET and (eye_tracker is not None) and (k in et_keys):

            if require_confirm:
                message_stim.text = (
                    f"EyeLink setup\n"
                    f"Press {k.upper()} again to confirm, any other key cancels."
                )
                message_stim.draw()
                win.flip()
                event.clearEvents()
                confirm = event.waitKeys()[0].lower()
                if confirm != k:
                    # Cancelled — redraw original message and keep waiting
                    message_stim.text = text
                    message_stim.draw()
                    win.flip()
                    event.clearEvents()
                    continue

            # --- Enter EyeLink setup (stop → setup → resume) ---
            try:
                try:
                    eye_tracker.stop_recording()
                except Exception:
                    pass

                try:
                    eye_tracker.set_offline_mode()
                except Exception:
                    pass

                # Opens the EyeLink camera/calibration/validation menu.
                # Experimenter presses Escape inside that menu to return here.
                eye_tracker.setup_tracker()

                try:
                    eye_tracker.start_recording()
                except Exception:
                    pass
                # ensure that mouse is invisible and key presses are registered during calibration when in fullscreen mode
                try:
                    win.winHandle.activate()
                    #win.flip()
                except Exception:
                    pass

            except Exception as exc:
                logging.warning(f"EyeLink setup failed (continuing): {exc}")

            # Redraw message and keep waiting — do NOT advance the experiment
            message_stim.text = text
            message_stim.draw()
            win.flip()
            event.clearEvents()
            kb.clearEvents()
            continue

        # ---------- Normal key: advance (with escape handling) ----------
        if k=="escape" and not allow_escape:
            print("Experiment ended")
            win.close()
            core.quit()
        return keys
       

# Creating a block
def create_block(trial_types, trials_per_block, rng=random):
    """Each trial type is drawn randomly and equally often within a block"""
    n_types = len(trial_types)
    if trials_per_block % n_types != 0:
        raise ValueError(
            f"trials_per_block ({trials_per_block}) must be divisible by "
            f"number of trial types ({n_types}) to ensure equal counts."
        )
    reps = trials_per_block // n_types
    block_list = trial_types * reps
    rng.shuffle(block_list)
    return block_list

# Running ITI also polling for presses and logging
def run_iti(win, kb, duration, fixation=None): 
    """ 
    Runs an ITI period that monitors and logs any key presses
    Shows fixation during the ITI

    Returns a dict with both raw and compact logs
    """
    kb.clearEvents()
    iti_clock = core.Clock()
    events= []

    win.flip()  # ensure any previous stimuli are cleared and we start with a fresh screen for the ITI

    while iti_clock.getTime() < duration:
        # check for resp_end and send trigger
        pending_resp_end(kb)
        # poll first so an Escape press can be logged before quitting
        presses = kb.getKeys(waitRelease=False, clear=True)
        if presses:
            t_ms = clock_ms(iti_clock)
            for p in presses:
                events.append({
                    "t_ms": t_ms,
                    "name": p.name,                    # can be None
                    "code": getattr(p, "code", None)    # fallback for unknown keycodes
                })
                  # indicate key press during ITI with red fixation   

        check_quit(win, kb)

        if fixation is not None:
            fixation.draw()
            win.flip()
        else:
            core.wait(0.001)
    
    kb.clearEvents()  # clear any presses that happened during the ITI before next trial starts
    
    iti_keypress = None
    iti_keypresstime = None
    if events:
        first = events[0]
        iti_keypress = first["name"] if first["name"] is not None else f"code_{first['code']}"
        iti_keypresstime = first["t_ms"]
    return {
        "iti_n" : len(events),
        "iti_keypress": iti_keypress,
        "iti_keypresstime": iti_keypresstime,
        "iti_events": events
    }
