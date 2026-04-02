import eyelinker
from psychopy import visual, core, event
from psychopy.hardware import keyboard
import logging
from datetime import datetime
import os



from config import blocks, trials_per_block, trial_types, messages, study_id
from constant_utils import check_quit, to_ms, show_message, create_block, clock_ms
from logging_utils import (
    make_data_folder,
    get_participant_deets,
    create_trial_writer,
    create_trigger_writer,
    append_demographics_row
)
from trial_logic import run_trial
from stimuli import Stimuli
from eeg_setup import eeg

# Logging set up: Demographics + trial + trigger events
demographics = get_participant_deets()
subjID = demographics["subjID"]
date_str = demographics["Date"]
session_start = demographics["Session_start"]
data_folder = make_data_folder(subjID)

# Window + Keyboard config
win = visual.Window(size=(800,600),fullscr=True, color='white', screen=0, units='pix')
mouse = event.Mouse(visible=False, win=win)
mouse.setVisible(False)
kb = keyboard.Keyboard()

# Stimuli
stim = Stimuli(win)
fixation = stim.fixation
stim_top = stim.stim_top
stim_bottom = stim.stim_bottom
message_stim = stim.message_stim
vpb_fill = stim.vpb_fill
vpb_outline = stim.vpb_outline


trial_fh, trial_writer = create_trial_writer(data_folder, study_id, subjID)
trigger_fh, trigger_writer = create_trigger_writer(data_folder, study_id, subjID)

# EEG setup
enable_eeg = False # when running exp in lab, change 
EEG, port =  eeg(enable_eeg=enable_eeg)

# Eye tracker set up (EyeLink)
# ── toggle this when moving between desk and lab ──────────────────────────
enable_et = False   # False → no hardware needed; True → connect to EyeLink
# ──────────────────────────────────────────────────────────────────────────

ET = False          # will be set True only if hardware connects successfully
et = None           # the EyeLinker object (ConnectedEyeLinker or MockEyeLinker)

if enable_et:
    try:
        # EDF filename on the HOST PC: max 12 characters INCLUDING ".edf"
        safe = "".join(ch for ch in str(subjID) if ch.isalnum())
        host_edf = (safe[-8:] if safe else "S0000000") + ".edf"   

        # EyeLinker() shows a "not connected" screen if no tracker is found.
        # The user can press R to retry, D for debug/mock mode, or Q to quit.
        et = eyelinker.EyeLinker(window=win, filename=host_edf, eye="RIGHT")

        # Full init sequence (graphics → open EDF → tracker settings → tracking settings)
        et.init_tracker()

        # Start recording immediately; a short delay is built into start_recording()
        et.start_recording()
        # ensure that mouse is invisible and key presses are registered during calibration when in fullscreen mode
        win.winHandle.activate()
        #win.flip()

        # ET=True only for a real (non-mock) connection
        ET = (et is not None) and (not getattr(et, "mock", False))
        logging.info(f"EyeLink ready. ET={ET}, EDF={host_edf}")

    except Exception as exc:
        # Catches Q-quit from eyelinker OR any unexpected hardware error.
        # The experiment can still run without eye-tracking.
        #traceback.print_exc()
        logging.error(f"EyeLink init failed: {exc}")
        et = None
        ET = False
        logging.warning("Continuing WITHOUT eye tracking.")


# Clock
exp_clock = core.Clock()

# Trigger writing
trigger_ctx = {
    "EEG": EEG,
    "port" : port,
    "to_ms": lambda: to_ms(exp_clock),
    "clock_ms": clock_ms,
    "trigger_writer": trigger_writer,
    "trigger_fh": trigger_fh,
    "ET": ET,
    "eye_tracker": et,
}

# Run blocks and trials

status = "completed" # part of demographics logging 

try:
    first_trial_row = True
    total_trials = blocks * trials_per_block
    global_trial = 0
    while True:
        keys=show_message(
        win, message_stim, fixation, kb, messages["CALIBRATION"],
        wait=True,
        allow_escape=False,
        allow_et_setup=True, ET=ET, eye_tracker=et,
        require_confirm=False
        )
        if keys and keys[0].lower()=="f9":
            break
            
    event.clearEvents()
    kb.clearEvents()
    
    show_message(
    win, message_stim, fixation, kb, messages["start"],
    wait=True,
    allow_escape=False
)
                 
    exp_clock.reset()
    event.clearEvents()
    kb.clearEvents()
    for b in range(1, blocks +1):
        check_quit(win, kb)

        show_message(
            win, message_stim, fixation, kb,
            messages["block_start"].format(block_num=b, total_blocks=blocks), wait=True
        )
        event.clearEvents()
        kb.clearEvents()

        
        fixation.autoDraw = True
        win.flip()
        #win.getMovieFrame()
        #win.saveMovieFrames(f"fixation_{b}.png")
        core.wait(1.0)
        win.flip()

        block_start_ms = to_ms(exp_clock)
        block_list = create_block(trial_types, trials_per_block)

        for t, trial_type in enumerate(block_list, start = 1):
            global_trial +=1
            row = run_trial(
                trial_type=trial_type,
                block_num=b,
                trial_in_block=t,
                block_start_ms=block_start_ms,
                global_trial=global_trial,
                win=win,
                fixation=fixation,
                kb=kb,
                exp_clock=exp_clock,
                stim_top=stim_top,
                stim_bottom=stim_bottom,
                vpb_fill=vpb_fill,
                vpb_outline=vpb_outline,
                trigger_ctx=trigger_ctx
            )

            trial_writer.writerow(row)
            trial_fh.flush()

        if blocks % 2 == 0 and b == (blocks // 2):
            show_message(
                win, message_stim, fixation, kb, messages["halfway"],
                wait=True,
                allow_escape=False
            )
            while True:
                keys= show_message(
                win, message_stim, fixation, kb, messages["calibration_question"],
                wait=True,
                allow_escape=False,
                allow_et_setup=True, ET=ET, eye_tracker=et,
                require_confirm=False
                )
                if keys and keys[0].lower()=="f9":
                    break
                

        if b < blocks:
            show_message(
                win, message_stim, fixation, kb,
                messages["block_end"].format(block_num=b, total_blocks=blocks), wait=True,
                allow_escape=False, allow_et_setup=True, ET=ET, eye_tracker=et, require_confirm=False
            )
            while True:
                keys=show_message(
                win, message_stim, fixation, kb, messages["calibration_question"],
                wait=True,
                allow_escape=False,
                allow_et_setup=True, ET=ET, eye_tracker=et,
                require_confirm=False
                )
                if keys and keys[0].lower()=="f9":
                    break
    show_message(win, message_stim, fixation, kb, messages["end"],allow_escape=True, wait=True)

    win.close()
    #core.quit()

except SystemExit:
    status = "aborted"

except Exception:
    status = "error"
    raise

finally:

    session_end = datetime.now().strftime("%H:%M:%S")

    append_demographics_row(data_folder,{
        "Study_ID": study_id,
        "Subject_ID": subjID,
        "Date": date_str,
        "Session_start": session_start,
        "Session_end": session_end,
        "Status": status,
        "Age": demographics["Age"],
        "Gender": demographics["Gender"],
        "Handedness": demographics["Handedness"],
        "Vision": demographics["Vision"],
    })

    if trial_fh: trial_fh.close()
    if trigger_fh: trigger_fh.close()

    try:
        if et is not None and (not getattr(et, "mock", False)):
            try:
                et.stop_recording()    # required delay included :contentReference[oaicite:8]{index=8}
            except Exception:
                pass

            try:
                et.close_edf()         # closes host EDF :contentReference[oaicite:9]{index=9}
            except Exception:
                pass

            # Transfer EDF from host to stimulus PC (can be long path/filename)
            try:
                et.transfer_edf(os.path.join(data_folder, f"et_{subjID}.edf"))  # must end with .edf :contentReference[oaicite:10]{index=10}
            except Exception as e:
                logging.warning(f"EDF transfer failed: {e}")

            try:
                et.close_connection()  # closes tracker + graphics :contentReference[oaicite:11]{index=11}
            except Exception:
                pass
    except Exception as e:
        logging.warning(f"EyeLink shutdown failed: {e}")