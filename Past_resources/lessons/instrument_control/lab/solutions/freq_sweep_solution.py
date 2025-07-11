import os
import numpy as np
from time import sleep
import siglent_sds1104xe_oscope_solution as osc 
import siglent_sdg2082x_fgen_solution as fgen
from simple_fft import simple_fft

def capture_freq_sweep(out_directory, osc_inst, fgen_inst, start_freq, end_freq, npoints, yscale):
    """
    Executes a frequency sweep. Iteratively sets the function generator frequency and captures 
    data from the oscilloscope, and saves each set of data. 

    :param out_directory: str, directory to save the data 
    :param osc_inst: oscilloscope pyvisa resource 
    :param fgen_inst: function generator pyvisa resource
    :param start_freq: float, starting frequency for the sweep 
    :param end_freq: float, ending frequency for the sweep 
    :param npoints: int, number of points in the sweep
    :param yscale: float, oscilloscope voltage per division in V / div
    """
    # initialize instruments
    osc.initialize(osc_inst)
    xscale = 'VARIABLE' 
    xoffset, yoffset = 0, 0
    amplification = 1 
    trigger_mode = 'AUTO'
    osc.set_yscale(osc_inst, yscale)
    inst_log = osc.create_log(xscale, xoffset, yscale, yoffset, amplification, trigger_mode) + '\n'
    
    fgen.initialize(fgen_inst)
    fgen.set_amplitude(fgen_inst, 1, 5)
    channel = 1 
    wave_type = 'SINE'
    freq = 'VARIABLE' 
    amp = 5 
    offset = 0
    inst_log += fgen.create_log(channel, wave_type, freq, amp, offset) + '\n'
    # set up frequency sweep    
    frequencies = np.geomspace(start_freq, end_freq, npoints)
    log = inst_log + "# --------- Geometric frequency sweep settings --------- #\n" 
    log += f'start frequency: {start_freq} Hz\n' 
    log += f'end frequency: {end_freq} Hz\n' 
    log += f'number of points: {npoints}\n'
    # save log file
    log_path = out_directory + 'freqsweep.log' 
    if os.path.exists(log_path):
        raise FileExistsError(f'{log_path} already exists')
    with open(log_path, 'w') as f:
        f.write(log)
    # execute frequency sweep
    sleep(0.5)
    fgen.set_channel_state(fgen_inst, 1, 'ON')
    sleep(5)
    for index, frequency in enumerate(frequencies):
        set_freq(fgen_inst, osc_inst, frequency)
        tsample, time, voltage = osc.capture_data(osc_inst) 
        np.save(out_directory + f'freqsweep_{index:03d}.npy', [time, voltage])
    fgen.set_channel_state(fgen_inst, 1, 'OFF')

def set_freq(fgen_inst, osc_inst, freq):
    """ 
    Sets the function generator to the given frequency and sets up the 
    oscilloscope x scale to roughly ten periods per division 

    :param freq: float, frequency in Hz 
    """
    # set frequency of function generator
    fgen.set_frequency(fgen_inst, 1, freq)
    # set xscale of oscilloscope
    tperiod = 1 / freq 
    xscale = tperiod * 10
    osc.set_xscale(osc_inst, xscale)
    # sleep
    sleep(0.1)

def get_freq_from_log(path):
    """
    Creates the frequency array corresponding to a geometric 
    frequency sweep from the log file.

    :param path: str, log path 

    :return frequencies: np.array, array of frequencies in Hz 
    """
    with open(path, 'r') as file:
        lines = file.readlines()
    fstart = [l for l in lines if l.startswith('start frequency: ')][0].replace('start frequency: ', '')
    fstart = float(fstart.replace(' Hz\n', ''))
    fend = [l for l in lines if l.startswith('end frequency: ')][0].replace('end frequency: ', '')
    fend = float(fend.replace(' Hz\n', ''))
    npoints = [l for l in lines if l.startswith('number of points: ')][0].replace('number of points: ', '')
    npoints = int(npoints.replace('\n', ''))
    frequencies = np.geomspace(fstart, fend, npoints)
    return frequencies

def import_freq_sweep(out_directory):
    """
    Import frequency sweep data and extract the transmission amplitude 

    :param frequencies: np.array, array of frequencies in Hz 
    :param out_directory: str, directory containing the data 
    :param amp: float, function generator output in V 

    :return good_freqs: np.array, array of frequencies from the data, with 
        bad data sets removed 
    :return transmission: np.array, array of transmission data         
    """
    frequencies = get_freq_from_log(out_directory + 'freqsweep.log')
    transmission = []
    good_freqs = []
    for index, frequency in enumerate(frequencies):
        time, voltage = np.load(out_directory + f'freqsweep_{index:03d}.npy') 
        if len(time):
            tsample = time[1] - time[0]
            f, y = simple_fft(tsample, voltage)
            ix = np.argmin(abs(f - frequency))
            transmission.append(y[ix])
            good_freqs.append(frequency)
    good_freqs, transmission = np.array(good_freqs), np.array(transmission)
    return good_freqs, transmission