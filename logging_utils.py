"""
This is for: 
1. getting participant demographic details 
2. saving participant demographic details in a csv file that gets updated every time a new participant is added
3. creating a trial events csv file for each participant

"""

import os
import logging
from datetime import datetime
import csv
from psychopy import gui, core
from config import study_id, demographics_fields, TRIAL_FIELDS, Cond_code, TRIGGER_FIELDS

def make_data_folder(subjID=None):
# Get CWD and create folder where data will be saved
    data_folder = os.path.join(os.getcwd(), "data")
    if subjID:
        data_folder = os.path.join(data_folder, subjID)
    os.makedirs(data_folder, exist_ok=True)
    return data_folder  

def get_participant_deets():
        # Dialog boxes for collecting demographic info 
    id ={"Subject ID (e.g., P001 or S001)": ""}
    dlg = gui.DlgFromDict(id, title="Participant Info (1/5)")
    if not dlg.OK:
        core.quit()
        raise SystemExit("Experiment cancelled by user.")

    subjID= str(id["Subject ID (e.g., P001 or S001)"]).strip()

    age={"Age": ""}
    dlg = gui.DlgFromDict(age, title="Participant Info (2/5)")
    if not dlg.OK:
        core.quit()
        raise SystemExit("Experiment cancelled by user.")
    logging.info("Age: %s", age["Age"])

    gender={"Gender": ["F","M", "Other", "Prefer not to say"]}
    dlg = gui.DlgFromDict(gender, title="Participant Info (3/5)")
    if not dlg.OK:
        core.quit()
        raise SystemExit("Experiment cancelled by user.")
    logging.info("Gender: %s", gender["Gender"])

    handedness={"Handedness": ["R", "L", "A"]}
    dlg= gui.DlgFromDict(handedness, title="Participant Info (4/5)")
    if not dlg.OK:
        core.quit()
        raise SystemExit("Experiment cancelled by user.")
    logging.info("Handedness: %s", handedness["Handedness"])

    vision ={"Vision" : ["Normal", "Corrected"]}
    dlg = gui.DlgFromDict(vision, title="Participant Info (5/5)")
    if not dlg.OK:
        core.quit()
        raise SystemExit("Experiment cancelled by user.")
    logging.info("Vision: %s", vision["Vision"])
    logging.info("")

    date_str = datetime.now().strftime("%d-%m-%Y")
    session_start = datetime.now().strftime("%H:%M:%S")

    return {
        "subjID": subjID,
        "Age": age["Age"],
        "Gender": gender["Gender"],
        "Handedness": handedness["Handedness"],
        "Vision": vision["Vision"],
        "Date": date_str,
        "Session_start": session_start
    }
    
def create_trial_writer(data_folder, study_id, subjID):

    trials_csv = os.path.join(
        data_folder,
        f"{study_id}_{subjID}.csv"
    )

    fh = open(trials_csv, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(fh, fieldnames=TRIAL_FIELDS)
    writer.writeheader()
    fh.flush()

    return fh, writer

def create_trigger_writer (data_folder, study_id, subjID):

    triggers_csv = os.path.join(
        data_folder,
        f"{study_id}_{subjID}_triggers.csv"
    )

    fh = open(triggers_csv, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(fh, fieldnames=TRIGGER_FIELDS)
    writer.writeheader()
    fh.flush()

    return fh, writer
    
def append_demographics_row(data_folder, row):
    demographics_csv = os.path.join(data_folder, "participants.csv")

    exists = os.path.exists(demographics_csv) and os.path.getsize(demographics_csv) > 0

    with open(demographics_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=demographics_fields)
        if not exists:
            w.writeheader()
        w.writerow(row)


