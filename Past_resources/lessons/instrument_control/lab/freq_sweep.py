""" freq_sweep.py:

This module implements frequency sweep data acquisition.

Version 1: <add your name>, <add the date>
"""
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
    # Your code here


def import_freq_sweep(out_directory, amp = 2.5):
    """
    Import frequency sweep data and extract the transmission amplitude 

    :param frequencies: np.array, array of frequencies in Hz 
    :param out_directory: str, directory containing the data 
    :param amp: float, function generator output in V 

    :return good_freqs: np.array, array of frequencies in Hz 
    :return transmission: np.array, array of transmission data         
    """
    # Your code here 