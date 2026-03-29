"""EEG tracker setup and configuration."""

import serial
import subprocess
import logging


def eeg(enable_eeg):

    port = None

    if enable_eeg:
        try:
            # set up port for triggers
            comport = subprocess.check_output('python C:\PROGS\detectbiosemiserial.py').strip().decode()
            port = serial.Serial(
                port=comport,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            logging.info("Shared Serial Port Initialized Successfully.")
        
            # start recording
            port.write(bytes([250])) 
        except Exception as e:
            logging.error(f"Error initializing EEG serial port: {e}")
            port = None


    return enable_eeg, port


