import logging
from config import EVENT_OFFSET

#To track response end 
WAITING_RESP_END = {
    "waiting_release" : False, # to track if we're waiting for a key release after response
    "key" : None,  # to track which key we're waiting to be released
    "on_release": None, # what to do when key is released
}

#For sending immediate triggers that don't rely on flips
def send_trigger_and_log(event_name, Cond_code, trial_type, EEG, port, to_ms, 
                         clock_ms, trial_clock= None, trigger_writer=None, msg= None, 
                         trigger_fh=None, block="", trial="", trial_global="",
                        ET=False, eye_tracker=None
                        ):
    if msg is None:
        msg = f"{event_name}_{trial_type}"
    cond_code = Cond_code[trial_type]
    trigger_code= EVENT_OFFSET[event_name] + cond_code
    exp_ms = to_ms()

    if trial_clock is not None:
        trial_ms = clock_ms(trial_clock)
    else:
        trial_ms = ""
    # send to EEG 
    if EEG and port is not None:
        port.write(bytes([trigger_code]))
    
    if ET and eye_tracker is not None:
        try:
            eye_tracker.send_message(f"trig{trigger_code}")
        except Exception as e:
            logging.warning(f"EyeLink send_message failed: {e}")

    logging.info(
        f"Trigger sent: code={trigger_code}, event={event_name},"
        f"Cond_code={cond_code}, exp_ms={exp_ms}, trial_ms={trial_ms},"
        f"block={block}, trial={trial}, trial_global={trial_global}, msg={msg}"
    ) 
    #CSV logging just to keep track of triggers sent (can delete later)
    if trigger_writer is not None:
        trigger_writer.writerow({
            "Block": block,
            "Trial": trial,
            "Trial_global": trial_global,
            "Cond_code": cond_code,
            "Event": event_name,
            "Trigger_code": trigger_code,
            "exp_ms": exp_ms,
            "trial_ms": trial_ms,
        })
        if trigger_fh is not None:
            trigger_fh.flush()

# Flip dependent triggers (e.g., R1_screen)
def trigger_on_flip(win, event_name, Cond_code, trial_type, EEG, port, to_ms, clock_ms, trial_clock = None, 
                    trigger_writer=None, msg= None, trigger_fh=None, block="", trial="", trial_global="", ET=False, eye_tracker=None):
    if msg is None:
        msg = f"{event_name}_{trial_type}"
    
    cond_code = Cond_code[trial_type]
    trigger_code = EVENT_OFFSET[event_name] + cond_code

    exp_box =[None]
    trial_box = [None]

    win.callOnFlip(lambda: exp_box.__setitem__(0, to_ms()))
    if trial_clock is not None:
        win.callOnFlip(lambda: trial_box.__setitem__(0, clock_ms(trial_clock)))

    if EEG and port is not None:
        win.callOnFlip(lambda: port.write(bytes([trigger_code])))
    
    # EyeLink message on the flip (eyelinker wrapper)
    if ET and eye_tracker is not None:
        win.callOnFlip(lambda: eye_tracker.send_message(f"trig{trigger_code}"))
        
    def after_flip_write():
        exp_ms = exp_box[0]
        trial_ms = trial_box[0] if trial_clock is not None else ""
        
        logging.info(
            f"Trigger sent (on flip): code={trigger_code}, event={event_name}, "
            f"Cond_code={cond_code}, exp_ms={exp_ms}, trial_ms={trial_ms}, " 
            f"block={block}, trial={trial}, trial_global={trial_global}, msg={msg}"
        )

        if trigger_writer is not None:
            trigger_writer.writerow({
                "Block": block,
                "Trial": trial,
                "Trial_global": trial_global,
                "Cond_code": cond_code,
                "Event": event_name,
                "Trigger_code": trigger_code,
                "exp_ms": exp_ms,
                "trial_ms": trial_ms,
            })
            if trigger_fh is not None:
                trigger_fh.flush()
           
    win.callOnFlip(after_flip_write)

# Waiting for a respond end to send trigger
def pending_resp_end(kb):
    if not WAITING_RESP_END["waiting_release"]:
        return 
    ups = kb.getKeys(keyList=[WAITING_RESP_END["key"]], waitRelease=True, clear = False)
    if not ups:
        return
    WAITING_RESP_END["on_release"]()
    WAITING_RESP_END["waiting_release"] = False
    WAITING_RESP_END["key"] = None
    WAITING_RESP_END["on_release"] = None
